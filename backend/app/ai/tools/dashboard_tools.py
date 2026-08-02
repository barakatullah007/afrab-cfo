from typing import Any

from sqlalchemy.orm import Session

from app.ai.tools._serialization import to_jsonable
from app.models.user import User
from app.services.dashboard_service import DashboardService


def get_dashboard_summary(
    db: Session,
    current_user: User,
    service: DashboardService,
) -> dict[str, Any]:
    """Return the authenticated user's dashboard summary.

    Args:
        db: Database session.
        current_user: Authenticated user.
        service: Dashboard business service.

    Returns:
        JSON-serializable dashboard summary.
    """

    return to_jsonable(
        service.get_summary(
            db,
            current_user,
        )
    )


def get_recent_transactions(
    db: Session,
    current_user: User,
    service: DashboardService,
) -> list[dict[str, Any]]:
    """Return recent dashboard transactions for the user.

    Args:
        db: Database session.
        current_user: Authenticated user.
        service: Dashboard business service.

    Returns:
        JSON-serializable recent transaction summaries.
    """

    return to_jsonable(
        service.get_recent_transactions(
            db,
            current_user,
        )
    )
