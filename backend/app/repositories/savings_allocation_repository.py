from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.savings_allocation import SavingsAllocation


class SavingsAllocationRepository:

    def save(
        self,
        db: Session,
        allocation: SavingsAllocation,
    ) -> SavingsAllocation:
        db.add(allocation)
        db.commit()
        db.refresh(allocation)
        return allocation

    def get_all(
        self,
        db: Session,
        user_id: int,
    ) -> list[SavingsAllocation]:
        return (
            db.query(SavingsAllocation)
            .filter(SavingsAllocation.user_id == user_id)
            .order_by(
                SavingsAllocation.year.desc(),
                SavingsAllocation.month.desc(),
                SavingsAllocation.created_at.desc(),
            )
            .all()
        )

    def get_by_id(
        self,
        db: Session,
        allocation_id: int,
        user_id: int,
    ) -> SavingsAllocation | None:
        return (
            db.query(SavingsAllocation)
            .filter(
                SavingsAllocation.id == allocation_id,
                SavingsAllocation.user_id == user_id,
            )
            .first()
        )

    def get_allocated_total(
        self,
        db: Session,
        user_id: int,
        month: int,
        year: int,
        exclude_allocation_id: int | None = None,
    ) -> Decimal:
        query = db.query(
            func.coalesce(
                func.sum(SavingsAllocation.amount),
                0,
            )
        ).filter(
            SavingsAllocation.user_id == user_id,
            SavingsAllocation.month == month,
            SavingsAllocation.year == year,
        )

        if exclude_allocation_id is not None:
            query = query.filter(SavingsAllocation.id != exclude_allocation_id)

        return Decimal(query.scalar())

    def delete(
        self,
        db: Session,
        allocation: SavingsAllocation,
    ) -> None:
        db.delete(allocation)
        db.commit()
