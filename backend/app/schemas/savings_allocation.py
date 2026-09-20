from datetime import datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
)

from app.enums.savings_allocation import SavingsAllocationType


class SavingsAllocationBase(BaseModel):

    allocation_type: SavingsAllocationType = Field(
        examples=["emergency_fund"],
    )

    amount: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
        examples=["5000.00"],
    )

    month: int = Field(
        ge=1,
        le=12,
        examples=[9],
    )

    year: int = Field(
        ge=2000,
        le=2100,
        examples=[2026],
    )

    name: str = Field(
        min_length=1,
        max_length=100,
        examples=["Emergency Fund"],
    )

    current_value: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
        examples=["3250.00"],
    )

    notes: str | None = Field(
        default=None,
        max_length=1000,
        examples=["September allocation"],
    )


class SavingsAllocationCreate(SavingsAllocationBase):
    pass


class SavingsAllocationUpdate(BaseModel):

    allocation_type: SavingsAllocationType | None = Field(
        default=None,
        examples=["investment"],
    )

    amount: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=12,
        decimal_places=2,
        examples=["3000.00"],
    )

    month: int | None = Field(
        default=None,
        ge=1,
        le=12,
        examples=[9],
    )

    year: int | None = Field(
        default=None,
        ge=2000,
        le=2100,
        examples=[2026],
    )

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        examples=["Investment"],
    )

    current_value: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
        examples=["3250.00"],
    )

    notes: str | None = Field(
        default=None,
        max_length=1000,
        examples=["Updated allocation"],
    )


class SavingsAllocationResponse(SavingsAllocationBase):

    id: int

    created_at: datetime

    updated_at: datetime

    @computed_field
    @property
    def gain_loss(self) -> Decimal | None:
        if (
            self.allocation_type != SavingsAllocationType.INVESTMENT
            or self.current_value is None
        ):
            return None

        return self.current_value - self.amount

    @computed_field
    @property
    def return_percentage(self) -> Decimal | None:
        gain_loss = self.gain_loss

        if (
            self.allocation_type != SavingsAllocationType.INVESTMENT
            or gain_loss is None
            or self.amount == 0
        ):
            return None

        return (gain_loss / self.amount) * Decimal("100")

    model_config = ConfigDict(
        from_attributes=True,
    )


class SavingsAllocationSummaryResponse(BaseModel):

    month: int

    year: int

    total_savings: Decimal

    total_allocated: Decimal

    remaining_savings: Decimal
