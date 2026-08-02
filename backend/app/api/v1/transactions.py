from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.transaction import (
    TransactionCreate,
    TransactionResponse,
)
from app.services.transaction_service import TransactionService

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"],
)

service = TransactionService()


@router.post(
    "",
    response_model=TransactionResponse,
    status_code=201,
)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
):
    return service.create_transaction(db, transaction)


@router.get(
    "",
    response_model=list[TransactionResponse],
)
def get_transactions(
    db: Session = Depends(get_db),
):
    return service.get_transactions(db)


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
):
    transaction = service.get_transaction(db, transaction_id)

    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found",
        )

    return transaction


@router.delete(
    "/{transaction_id}",
    status_code=204,
)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
):
    transaction = service.delete_transaction(
        db,
        transaction_id,
    )

    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found",
        )