from datetime import datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class TransactionCreate(BaseModel):

    account_id: int = Field(
        gt=0,
        examples=[1],
    )

    category_id: int = Field(
        gt=0,
        examples=[1],
    )

    description: str = Field(
        min_length=1,
        max_length=255,
        examples=["Lunch"],
    )

    merchant: str | None = Field(
        default=None,
        max_length=150,
        examples=["KFC"],
    )

    amount: Decimal = Field(
        gt=0,
        decimal_places=2,
        examples=[250.00],
    )

    notes: str | None = Field(
        default=None,
        max_length=1000,
        examples=["Lunch with client"],
    )

    transaction_date: datetime = Field(
        examples=["2026-08-02T13:30:00Z"],
    )


class TransactionUpdate(BaseModel):

    account_id: int = Field(
        gt=0,
        examples=[1],
    )

    category_id: int = Field(
        gt=0,
        examples=[2],
    )

    description: str = Field(
        min_length=1,
        max_length=255,
        examples=["Dinner"],
    )

    merchant: str | None = Field(
        default=None,
        max_length=150,
        examples=["Domino's"],
    )

    amount: Decimal = Field(
        gt=0,
        decimal_places=2,
        examples=[600.00],
    )

    notes: str | None = Field(
        default=None,
        max_length=1000,
        examples=["Dinner with friends"],
    )

    transaction_date: datetime = Field(
        examples=["2026-08-02T20:15:00Z"],
    )


class TransactionResponse(BaseModel):

    id: int

    account_id: int

    category_id: int

    description: str

    merchant: str | None

    amount: Decimal

    notes: str | None

    transaction_date: datetime

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )