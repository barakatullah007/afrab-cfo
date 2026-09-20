from typing import Any

from sqlalchemy.orm import Session

from app.ai.advisors.budget_advisor import BudgetAdvisor
from app.ai.advisors.financial_health_advisor import FinancialHealthAdvisor
from app.ai.advisors.goal_advisor import GoalAdvisor
from app.ai.advisors.savings_advisor import SavingsAdvisor
from app.ai.advisors.spending_advisor import SpendingAdvisor
from app.ai.tools import financial_tools, recurring_tools
from app.ai.tools._serialization import to_jsonable
from app.models.user import User
from app.services.financial_intelligence_service import (
    FinancialIntelligenceService,
)
from app.services.recurring_transaction_service import (
    RecurringTransactionService,
)


def get_financial_health(
    db: Session,
    current_user: User,
    financial_service: FinancialIntelligenceService,
    recurring_service: RecurringTransactionService,
) -> dict[str, Any]:
    """Return financial health score and recommendations."""

    advisor = FinancialHealthAdvisor()

    return to_jsonable(
        advisor.analyze(
            summary=financial_tools.get_financial_summary(
                db,
                current_user,
                financial_service,
            ),
            budget_utilization=financial_tools.get_budget_utilization(
                db,
                current_user,
                financial_service,
            ),
            goal_progress=financial_tools.get_goal_progress(
                db,
                current_user,
                financial_service,
            ),
            cash_flow=financial_tools.get_monthly_cashflow(
                db,
                current_user,
                financial_service,
            ),
            recurring_transactions=recurring_tools.get_recurring_transactions(
                db,
                current_user,
                recurring_service,
            ),
        )
    )


def get_spending_analysis(
    db: Session,
    current_user: User,
    financial_service: FinancialIntelligenceService,
) -> dict[str, Any]:
    """Return spending analysis and recommendations."""

    advisor = SpendingAdvisor()

    return to_jsonable(
        advisor.analyze(
            category_insights=financial_tools.get_category_insights(
                db,
                current_user,
                financial_service,
            ),
            monthly_cashflow=financial_tools.get_monthly_cashflow(
                db,
                current_user,
                financial_service,
            ),
            budget_utilization=financial_tools.get_budget_utilization(
                db,
                current_user,
                financial_service,
            ),
        )
    )


def get_budget_advice(
    db: Session,
    current_user: User,
    financial_service: FinancialIntelligenceService,
) -> dict[str, Any]:
    """Return budget advice."""

    advisor = BudgetAdvisor()

    return to_jsonable(
        advisor.analyze(
            financial_tools.get_budget_utilization(
                db,
                current_user,
                financial_service,
            )
        )
    )


def get_goal_advice(
    db: Session,
    current_user: User,
    financial_service: FinancialIntelligenceService,
) -> dict[str, Any]:
    """Return goal prioritization and contribution advice."""

    advisor = GoalAdvisor()

    return to_jsonable(
        advisor.analyze(
            financial_tools.get_goal_progress(
                db,
                current_user,
                financial_service,
            )
        )
    )


def get_savings_advice(
    db: Session,
    current_user: User,
    financial_service: FinancialIntelligenceService,
) -> dict[str, Any]:
    """Return savings advice."""

    advisor = SavingsAdvisor()

    return to_jsonable(
        advisor.analyze(
            summary=financial_tools.get_financial_summary(
                db,
                current_user,
                financial_service,
            ),
            monthly_cashflow=financial_tools.get_monthly_cashflow(
                db,
                current_user,
                financial_service,
            ),
        )
    )
