from typing import Any

from sqlalchemy.orm import Session

from app.ai.tools._serialization import to_jsonable
from app.models.user import User
from app.services.financial_intelligence_service import (
    FinancialIntelligenceService,
)
from app.services.goal_service import GoalService


def get_goals(
    db: Session,
    current_user: User,
    service: GoalService,
) -> list[dict[str, Any]]:
    """Return goals owned by the authenticated user.

    Args:
        db: Database session.
        current_user: Authenticated user.
        service: Goal business service.

    Returns:
        JSON-serializable goal records.
    """

    return to_jsonable(
        service.get_goals(
            db,
            current_user,
        )
    )


def get_goal_progress(
    db: Session,
    current_user: User,
    service: FinancialIntelligenceService,
) -> list[dict[str, Any]]:
    """Return goal progress insights.

    Args:
        db: Database session.
        current_user: Authenticated user.
        service: Financial intelligence service.

    Returns:
        JSON-serializable goal progress insights.
    """

    return to_jsonable(
        service.get_goal_progress(
            db,
            current_user,
        )
    )
