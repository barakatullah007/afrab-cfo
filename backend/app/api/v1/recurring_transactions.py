from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.session import get_db
from app.dependencies.services import get_recurring_transaction_service
from app.models.user import User
from app.schemas.recurring_transaction import (
    RecurringTransactionCreate,
    RecurringTransactionResponse,
    RecurringTransactionUpdate,
)
from app.services.recurring_transaction_service import (
    RecurringTransactionService,
)

router = APIRouter(
    prefix="/recurring-transactions",
    tags=["Recurring Transactions"],
)


@router.post(
    "",
    response_model=RecurringTransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_recurring_transaction(
    recurring_transaction: RecurringTransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: RecurringTransactionService = Depends(
        get_recurring_transaction_service
    ),
):
    try:
        return service.create_recurring_transaction(
            db,
            current_user,
            recurring_transaction,
        )
    except ValueError as exc:
        raise _recurring_transaction_http_exception(exc)


@router.get(
    "",
    response_model=list[RecurringTransactionResponse],
)
def get_recurring_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: RecurringTransactionService = Depends(
        get_recurring_transaction_service
    ),
):
    return service.get_recurring_transactions(
        db,
        current_user,
    )


@router.get(
    "/{recurring_transaction_id}",
    response_model=RecurringTransactionResponse,
)
def get_recurring_transaction(
    recurring_transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: RecurringTransactionService = Depends(
        get_recurring_transaction_service
    ),
):
    recurring_transaction = service.get_recurring_transaction(
        db,
        recurring_transaction_id,
        current_user,
    )

    if recurring_transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurring transaction not found",
        )

    return recurring_transaction


@router.put(
    "/{recurring_transaction_id}",
    response_model=RecurringTransactionResponse,
)
def update_recurring_transaction(
    recurring_transaction_id: int,
    recurring_transaction: RecurringTransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: RecurringTransactionService = Depends(
        get_recurring_transaction_service
    ),
):
    try:
        updated = service.update_recurring_transaction(
            db,
            recurring_transaction_id,
            current_user,
            recurring_transaction,
        )

        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recurring transaction not found",
            )

        return updated

    except ValueError as exc:
        raise _recurring_transaction_http_exception(exc)


@router.delete(
    "/{recurring_transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_recurring_transaction(
    recurring_transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: RecurringTransactionService = Depends(
        get_recurring_transaction_service
    ),
):
    deleted = service.delete_recurring_transaction(
        db,
        recurring_transaction_id,
        current_user,
    )

    if deleted is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurring transaction not found",
        )


@router.patch(
    "/{recurring_transaction_id}/activate",
    response_model=RecurringTransactionResponse,
)
def activate_recurring_transaction(
    recurring_transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: RecurringTransactionService = Depends(
        get_recurring_transaction_service
    ),
):
    recurring_transaction = service.activate_recurring_transaction(
        db,
        recurring_transaction_id,
        current_user,
    )

    if recurring_transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurring transaction not found",
        )

    return recurring_transaction


def _recurring_transaction_http_exception(
    exc: ValueError,
) -> HTTPException:
    if str(exc) in {
        "Account not found.",
        "Category not found.",
    }:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(exc),
    )


@router.patch(
    "/{recurring_transaction_id}/deactivate",
    response_model=RecurringTransactionResponse,
)
def deactivate_recurring_transaction(
    recurring_transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: RecurringTransactionService = Depends(
        get_recurring_transaction_service
    ),
):
    recurring_transaction = service.deactivate_recurring_transaction(
        db,
        recurring_transaction_id,
        current_user,
    )

    if recurring_transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurring transaction not found",
        )

    return recurring_transaction
