from datetime import datetime
from decimal import Decimal
from typing import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from app.enums.recurring_transaction import (
    RecurringFrequency,
    RecurringTransactionType,
)


class RecurringTransactionBase(BaseModel):

    account_id: int = Field(
        gt=0,
        examples=[1],
    )

    category_id: int = Field(
        gt=0,
        examples=[1],
    )

    title: str = Field(
        min_length=1,
        max_length=100,
        examples=["Monthly Salary"],
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
        examples=["Salary credited on the first day of each month"],
    )

    amount: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
        examples=["75000.00"],
    )

    transaction_type: RecurringTransactionType

    frequency: RecurringFrequency

    start_date: datetime = Field(
        examples=["2026-08-02T00:00:00Z"],
    )

    end_date: datetime | None = Field(
        default=None,
        examples=["2027-08-02T00:00:00Z"],
    )

    next_run_date: datetime = Field(
        examples=["2026-09-02T00:00:00Z"],
    )

    @model_validator(mode="after")
    def validate_dates(self) -> Self:
        if self.end_date is not None and self.end_date < self.start_date:
            raise ValueError(
                "End date cannot be before start date."
            )

        if self.next_run_date < self.start_date:
            raise ValueError(
                "Next run date cannot be before start date."
            )

        return self


class RecurringTransactionCreate(RecurringTransactionBase):
    pass


class RecurringTransactionUpdate(RecurringTransactionBase):
    is_active: bool = Field(
        default=True,
        examples=[True],
    )


class RecurringTransactionResponse(RecurringTransactionBase):

    id: int

    is_active: bool

    last_executed_at: datetime | None

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
