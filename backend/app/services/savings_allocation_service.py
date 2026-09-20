from decimal import Decimal

from sqlalchemy.orm import Session

from app.enums.savings_allocation import SavingsAllocationType
from app.models.savings_allocation import SavingsAllocation
from app.models.user import User
from app.repositories.savings_allocation_repository import (
    SavingsAllocationRepository,
)
from app.schemas.savings_allocation import (
    SavingsAllocationCreate,
    SavingsAllocationSummaryResponse,
    SavingsAllocationUpdate,
)
from app.services.financial_intelligence_service import (
    FinancialIntelligenceService,
)


class SavingsAllocationService:

    def __init__(self):
        self.repository = SavingsAllocationRepository()
        self.financial_intelligence_service = FinancialIntelligenceService()

    def create_allocation(
        self,
        db: Session,
        current_user: User,
        allocation_data: SavingsAllocationCreate,
    ) -> SavingsAllocation:
        self._validate_available_savings(
            db=db,
            user_id=current_user.id,
            month=allocation_data.month,
            year=allocation_data.year,
            amount=allocation_data.amount,
        )

        allocation = SavingsAllocation(
            user_id=current_user.id,
            allocation_type=allocation_data.allocation_type,
            amount=allocation_data.amount,
            month=allocation_data.month,
            year=allocation_data.year,
            name=allocation_data.name,
            current_value=self._resolve_current_value(
                allocation_data.allocation_type,
                allocation_data.amount,
                allocation_data.current_value,
            ),
            notes=allocation_data.notes,
        )

        return self.repository.save(
            db,
            allocation,
        )

    def get_allocations(
        self,
        db: Session,
        current_user: User,
    ) -> list[SavingsAllocation]:
        return self.repository.get_all(
            db,
            current_user.id,
        )

    def get_allocation(
        self,
        db: Session,
        allocation_id: int,
        current_user: User,
    ) -> SavingsAllocation | None:
        return self.repository.get_by_id(
            db,
            allocation_id,
            current_user.id,
        )

    def update_allocation(
        self,
        db: Session,
        allocation_id: int,
        current_user: User,
        allocation_data: SavingsAllocationUpdate,
    ) -> SavingsAllocation | None:
        allocation = self.repository.get_by_id(
            db,
            allocation_id,
            current_user.id,
        )

        if allocation is None:
            return None

        update_data = allocation_data.model_dump(
            exclude_unset=True,
        )

        allocation_type = update_data.get(
            "allocation_type",
            allocation.allocation_type,
        )
        amount = update_data.get(
            "amount",
            allocation.amount,
        )
        month = update_data.get(
            "month",
            allocation.month,
        )
        year = update_data.get(
            "year",
            allocation.year,
        )

        self._validate_available_savings(
            db=db,
            user_id=current_user.id,
            month=month,
            year=year,
            amount=amount,
            exclude_allocation_id=allocation.id,
        )

        for field in (
            "allocation_type",
            "amount",
            "month",
            "year",
            "name",
            "notes",
        ):
            if field in update_data:
                setattr(
                    allocation,
                    field,
                    update_data[field],
                )

        current_value = (
            update_data["current_value"]
            if "current_value" in update_data
            else allocation.current_value
        )

        allocation.current_value = self._resolve_current_value(
            allocation_type,
            amount,
            current_value,
        )

        return self.repository.save(
            db,
            allocation,
        )

    def delete_allocation(
        self,
        db: Session,
        allocation_id: int,
        current_user: User,
    ) -> SavingsAllocation | None:
        allocation = self.repository.get_by_id(
            db,
            allocation_id,
            current_user.id,
        )

        if allocation is None:
            return None

        self.repository.delete(
            db,
            allocation,
        )

        return allocation

    def get_monthly_allocated_total(
        self,
        db: Session,
        current_user: User,
        month: int,
        year: int,
    ) -> Decimal:
        return self.repository.get_allocated_total(
            db,
            current_user.id,
            month,
            year,
        )

    def get_remaining_savings(
        self,
        db: Session,
        current_user: User,
        month: int,
        year: int,
    ) -> Decimal:
        income, expense = (
            self.financial_intelligence_service.get_monthly_totals_for_month(
                db,
                current_user.id,
                month,
                year,
            )
        )
        total_allocated = self.get_monthly_allocated_total(
            db,
            current_user,
            month,
            year,
        )

        return income - expense - total_allocated

    def get_monthly_summary(
        self,
        db: Session,
        current_user: User,
        month: int,
        year: int,
    ) -> SavingsAllocationSummaryResponse:
        income, expense = (
            self.financial_intelligence_service.get_monthly_totals_for_month(
                db,
                current_user.id,
                month,
                year,
            )
        )
        total_savings = income - expense
        total_allocated = self.get_monthly_allocated_total(
            db,
            current_user,
            month,
            year,
        )

        return SavingsAllocationSummaryResponse(
            month=month,
            year=year,
            total_savings=total_savings,
            total_allocated=total_allocated,
            remaining_savings=total_savings - total_allocated,
        )

    def _validate_available_savings(
        self,
        db: Session,
        user_id: int,
        month: int,
        year: int,
        amount: Decimal,
        exclude_allocation_id: int | None = None,
    ) -> None:
        income, expense = (
            self.financial_intelligence_service.get_monthly_totals_for_month(
                db,
                user_id,
                month,
                year,
            )
        )
        total_savings = income - expense
        already_allocated = self.repository.get_allocated_total(
            db,
            user_id,
            month,
            year,
            exclude_allocation_id,
        )

        if already_allocated + amount > total_savings:
            raise ValueError(
                "Allocation exceeds available savings for this month."
            )

    def _resolve_current_value(
        self,
        allocation_type: SavingsAllocationType,
        amount: Decimal,
        current_value: Decimal | None,
    ) -> Decimal | None:
        if allocation_type == SavingsAllocationType.INVESTMENT:
            return current_value if current_value is not None else amount

        return None
