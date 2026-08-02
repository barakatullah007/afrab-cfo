from app.services.account_service import AccountService
from app.services.budget_service import BudgetService
from app.services.category_service import CategoryService
from app.services.dashboard_service import DashboardService
from app.services.financial_intelligence_service import (
    FinancialIntelligenceService,
)
from app.services.goal_service import GoalService
from app.services.recurring_transaction_service import (
    RecurringTransactionService,
)
from app.services.transaction_service import TransactionService
from app.services.user_service import UserService


def get_account_service() -> AccountService:
    return AccountService()


def get_budget_service() -> BudgetService:
    return BudgetService()


def get_category_service() -> CategoryService:
    return CategoryService()


def get_dashboard_service() -> DashboardService:
    return DashboardService()


def get_financial_intelligence_service() -> FinancialIntelligenceService:
    return FinancialIntelligenceService()


def get_goal_service() -> GoalService:
    return GoalService()


def get_recurring_transaction_service() -> RecurringTransactionService:
    return RecurringTransactionService()


def get_transaction_service() -> TransactionService:
    return TransactionService()


def get_user_service() -> UserService:
    return UserService()
