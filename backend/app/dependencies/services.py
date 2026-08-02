from app.services.account_service import AccountService
from app.services.category_service import CategoryService
from app.services.dashboard_service import DashboardService
from app.services.transaction_service import TransactionService
from app.services.user_service import UserService


def get_user_service() -> UserService:
    return UserService()


def get_account_service() -> AccountService:
    return AccountService()


def get_category_service() -> CategoryService:
    return CategoryService()


def get_transaction_service() -> TransactionService:
    return TransactionService()


def get_dashboard_service() -> DashboardService:
    return DashboardService()