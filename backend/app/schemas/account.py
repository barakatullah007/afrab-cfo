from datetime import datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from app.enums.account import AccountType


class AccountCreate(BaseModel):

    name: str = Field(
        min_length=1,
        max_length=100,
        examples=["Cash Wallet"],
    )

    type: AccountType

    opening_balance: Decimal = Field(
        ge=0,
        decimal_places=2,
        examples=[5000.00],
    )

    currency: str = Field(
        min_length=3,
        max_length=10,
        examples=["INR"],
    )

    icon: str = Field(
        min_length=1,
        max_length=100,
        examples=["fa-solid fa-wallet"],
    )

    color: str = Field(
        min_length=4,
        max_length=20,
        examples=["#22c55e"],
    )


class AccountUpdate(BaseModel):

    name: str = Field(
        min_length=1,
        max_length=100,
        examples=["HDFC Bank"],
    )

    type: AccountType

    opening_balance: Decimal = Field(
        ge=0,
        decimal_places=2,
        examples=[12000.00],
    )

    currency: str = Field(
        min_length=3,
        max_length=10,
        examples=["INR"],
    )

    icon: str = Field(
        min_length=1,
        max_length=100,
        examples=["fa-solid fa-building-columns"],
    )

    color: str = Field(
        min_length=4,
        max_length=20,
        examples=["#2563eb"],
    )


class AccountResponse(BaseModel):

    id: int

    name: str

    type: AccountType

    opening_balance: Decimal

    currency: str

    icon: str

    color: str

    is_default: bool

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )