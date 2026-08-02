from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class TransactionCreate(BaseModel):
    description: str = Field(
        min_length=1,
        max_length=255,
        examples=["Groceries"],
    )

    amount: Decimal = Field(
        gt=0,
        examples=[550.75],
    )


class TransactionUpdate(BaseModel):
    description: str = Field(
        min_length=1,
        max_length=255,
        examples=["Electricity Bill"],
    )

    amount: Decimal = Field(
        gt=0,
        examples=[1200],
    )


class TransactionResponse(BaseModel):
    id: int
    description: str
    amount: Decimal
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )