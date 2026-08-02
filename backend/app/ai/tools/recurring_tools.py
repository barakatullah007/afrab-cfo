from typing import Any

from sqlalchemy.orm import Session

from app.ai.tools._serialization import to_jsonable
from app.models.user import User
from app.services.recurring_transaction_service import (
    RecurringTransactionService,
)


def get_recurring_transactions(
    db: Session,
    current_user: User,
    service: RecurringTransactionService,
) -> list[dict[str, Any]]:
    """Return recurring transactions owned by the authenticated user.

    Args:
        db: Database session.
        current_user: Authenticated user.
        service: Recurring transaction business service.

    Returns:
        JSON-serializable recurring transaction records.
    """

    return to_jsonable(
        service.get_recurring_transactions(
            db,
            current_user,
        )
    )


def get_recurring_transaction(
    recurring_transaction_id: int,
    db: Session,
    current_user: User,
    service: RecurringTransactionService,
) -> dict[str, Any] | None:
    """Return one recurring transaction owned by the user.

    Args:
        recurring_transaction_id: Recurring transaction identifier.
        db: Database session.
        current_user: Authenticated user.
        service: Recurring transaction business service.

    Returns:
        JSON-serializable recurring transaction record, or None.
    """

    return to_jsonable(
        service.get_recurring_transaction(
            db,
            recurring_transaction_id,
            current_user,
        )
    )
