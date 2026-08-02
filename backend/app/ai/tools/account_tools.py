from typing import Any

from sqlalchemy.orm import Session

from app.ai.tools._serialization import to_jsonable
from app.models.user import User
from app.services.account_service import AccountService


def get_accounts(
    db: Session,
    current_user: User,
    service: AccountService,
) -> list[dict[str, Any]]:
    """Return accounts owned by the authenticated user.

    Args:
        db: Database session.
        current_user: Authenticated user.
        service: Account business service.

    Returns:
        JSON-serializable account records.
    """

    return to_jsonable(
        service.get_accounts(
            db,
            current_user,
        )
    )


def get_account(
    account_id: int,
    db: Session,
    current_user: User,
    service: AccountService,
) -> dict[str, Any] | None:
    """Return a single account owned by the authenticated user.

    Args:
        account_id: Account identifier.
        db: Database session.
        current_user: Authenticated user.
        service: Account business service.

    Returns:
        JSON-serializable account record, or None when not found.
    """

    return to_jsonable(
        service.get_account(
            db,
            account_id,
            current_user,
        )
    )
