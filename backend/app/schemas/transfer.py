from datetime import datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class TransferCreate(BaseModel):

    source_account_id: int = Field(
        gt=0,
        examples=[1],
    )

    destination_account_id: int = Field(
        gt=0,
        examples=[2],
    )

    amount: Decimal = Field(
        gt=0,
        decimal_places=2,
        examples=[3000.00],
    )

    description: str | None = Field(
        default=None,
        max_length=255,
        examples=["Transfer to savings"],
    )

    transfer_date: datetime = Field(
        examples=["2026-09-20T20:00:00Z"],
    )


class TransferResponse(BaseModel):

    id: int

    source_account_id: int

    destination_account_id: int

    amount: Decimal

    description: str | None

    transfer_date: datetime

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )