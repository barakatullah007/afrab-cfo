from typing import Any

from sqlalchemy.orm import Session

from app.ai.tools._serialization import to_jsonable
from app.models.user import User
from app.services.financial_intelligence_service import (
    FinancialIntelligenceService,
)


def get_financial_summary(
    db: Session,
    current_user: User,
    service: FinancialIntelligenceService,
) -> dict[str, Any]:
    """Return high-level financial intelligence summary.

    Args:
        db: Database session.
        current_user: Authenticated user.
        service: Financial intelligence service.

    Returns:
        JSON-serializable financial summary.
    """

    return to_jsonable(
        service.get_summary(
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


def get_category_insights(
    db: Session,
    current_user: User,
    service: FinancialIntelligenceService,
) -> list[dict[str, Any]]:
    """Return current-month category spending insights.

    Args:
        db: Database session.
        current_user: Authenticated user.
        service: Financial intelligence service.

    Returns:
        JSON-serializable category insights.
    """

    return to_jsonable(
        service.get_category_insights(
            db,
            current_user,
        )
    )


def get_monthly_cashflow(
    db: Session,
    current_user: User,
    service: FinancialIntelligenceService,
) -> dict[str, Any]:
    """Return current-month income, expense, and cash flow.

    Args:
        db: Database session.
        current_user: Authenticated user.
        service: Financial intelligence service.

    Returns:
        JSON-serializable monthly cashflow.
    """

    return to_jsonable(
        service.get_monthly_cashflow(
            db,
            current_user,
        )
    )
