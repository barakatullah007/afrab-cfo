from typing import Any

from sqlalchemy.orm import Session

from app.ai.tools._serialization import to_jsonable
from app.models.user import User
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
)
from app.services.transaction_service import TransactionService


def get_transactions(
    db: Session,
    current_user: User,
    service: TransactionService,
) -> list[dict[str, Any]]:
    """Return transactions owned by the authenticated user.

    Args:
        db: Database session.
        current_user: Authenticated user.
        service: Transaction business service.

    Returns:
        JSON-serializable transaction records.
    """

    return to_jsonable(
        service.get_transactions(
            db,
            current_user,
        )
    )


def get_transaction(
    transaction_id: int,
    db: Session,
    current_user: User,
    service: TransactionService,
) -> dict[str, Any] | None:
    """Return one transaction owned by the authenticated user.

    Args:
        transaction_id: Transaction identifier.
        db: Database session.
        current_user: Authenticated user.
        service: Transaction business service.

    Returns:
        JSON-serializable transaction record, or None when not found.
    """

    return to_jsonable(
        service.get_transaction(
            db,
            transaction_id,
            current_user,
        )
    )


def create_transaction(
    transaction: TransactionCreate,
    db: Session,
    current_user: User,
    service: TransactionService,
) -> dict[str, Any]:
    """Create a transaction through the business service.

    Args:
        transaction: Validated transaction payload.
        db: Database session.
        current_user: Authenticated user.
        service: Transaction business service.

    Returns:
        JSON-serializable created transaction record.
    """

    return to_jsonable(
        service.create_transaction(
            db,
            current_user,
            transaction,
        )
    )


def update_transaction(
    transaction_id: int,
    transaction: TransactionUpdate,
    db: Session,
    current_user: User,
    service: TransactionService,
) -> dict[str, Any] | None:
    """Update a transaction through the business service.

    Args:
        transaction_id: Transaction identifier.
        transaction: Validated transaction payload.
        db: Database session.
        current_user: Authenticated user.
        service: Transaction business service.

    Returns:
        JSON-serializable updated transaction, or None when not found.
    """

    return to_jsonable(
        service.update_transaction(
            db,
            transaction_id,
            current_user,
            transaction,
        )
    )
