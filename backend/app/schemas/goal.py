from datetime import datetime
from decimal import Decimal
from typing import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from app.enums.goal import (
    GoalPriority,
    GoalStatus,
)


class GoalBase(BaseModel):

    name: str = Field(
        min_length=1,
        max_length=100,
        examples=["Emergency Fund"],
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
        examples=["Six months of essential expenses"],
    )

    target_amount: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
        examples=["100000.00"],
    )

    current_amount: Decimal = Field(
        default=Decimal("0.00"),
        ge=0,
        max_digits=12,
        decimal_places=2,
        examples=["25000.00"],
    )

    target_date: datetime | None = Field(
        default=None,
        examples=["2027-08-02T00:00:00Z"],
    )

    priority: GoalPriority = Field(
        default=GoalPriority.MEDIUM,
        examples=["medium"],
    )

    status: GoalStatus = Field(
        default=GoalStatus.ACTIVE,
        examples=["active"],
    )

    @model_validator(mode="after")
    def validate_current_amount(self) -> Self:
        if self.current_amount > self.target_amount:
            raise ValueError(
                "Current amount cannot exceed target amount."
            )

        return self


class GoalCreate(GoalBase):
    pass


class GoalUpdate(GoalBase):
    pass


class GoalResponse(GoalBase):

    id: int

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
