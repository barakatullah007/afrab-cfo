from typing import Any

from sqlalchemy.orm import Session

from app.ai.tools._serialization import to_jsonable
from app.models.user import User
from app.services.budget_service import BudgetService
from app.services.financial_intelligence_service import (
    FinancialIntelligenceService,
)


def get_budgets(
    db: Session,
    current_user: User,
    service: BudgetService,
) -> list[dict[str, Any]]:
    """Return budgets owned by the authenticated user.

    Args:
        db: Database session.
        current_user: Authenticated user.
        service: Budget business service.

    Returns:
        JSON-serializable budget records.
    """

    return to_jsonable(
        service.get_budgets(
            db,
            current_user,
        )
    )


def get_budget_utilization(
    db: Session,
    current_user: User,
    service: FinancialIntelligenceService,
) -> list[dict[str, Any]]:
    """Return current-month budget utilization insights.

    Args:
        db: Database session.
        current_user: Authenticated user.
        service: Financial intelligence service.

    Returns:
        JSON-serializable budget utilization insights.
    """

    return to_jsonable(
        service.get_budget_utilization(
            db,
            current_user,
        )
    )
