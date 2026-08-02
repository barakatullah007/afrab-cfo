from datetime import datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class BudgetBase(BaseModel):

    category_id: int = Field(
        gt=0,
        examples=[1],
    )

    month: int = Field(
        ge=1,
        le=12,
        examples=[8],
    )

    year: int = Field(
        ge=2000,
        le=2100,
        examples=[2026],
    )

    amount: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
        examples=["25000.00"],
    )


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BudgetBase):
    pass


class BudgetResponse(BudgetBase):

    id: int

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )
