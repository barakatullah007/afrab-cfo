from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.enums.category import CategoryType
from app.models.account import Account
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.dashboard_recent import DashboardRecentTransaction
from app.schemas.dashboard_summary import DashboardSummary


class DashboardService:

    def get_summary(
        self,
        db: Session,
        current_user: User,
    ) -> DashboardSummary:

        total_balance = (
            db.query(
                func.coalesce(
                    func.sum(Account.opening_balance),
                    0,
                )
            )
            .filter(
                Account.user_id == current_user.id,
            )
            .scalar()
        )

        monthly_income = (
            db.query(
                func.coalesce(
                    func.sum(Transaction.amount),
                    0,
                )
            )
            .join(
                Category,
                Transaction.category_id == Category.id,
            )
            .filter(
                Transaction.user_id == current_user.id,
                Category.type == CategoryType.INCOME,
            )
            .scalar()
        )

        monthly_expense = (
            db.query(
                func.coalesce(
                    func.sum(Transaction.amount),
                    0,
                )
            )
            .join(
                Category,
                Transaction.category_id == Category.id,
            )
            .filter(
                Transaction.user_id == current_user.id,
                Category.type == CategoryType.EXPENSE,
            )
            .scalar()
        )

        total_balance = Decimal(total_balance)
        monthly_income = Decimal(monthly_income)
        monthly_expense = Decimal(monthly_expense)

        return DashboardSummary(
            total_balance=total_balance,
            monthly_income=monthly_income,
            monthly_expense=monthly_expense,
            savings=monthly_income - monthly_expense,
        )

    def get_recent_transactions(
        self,
        db: Session,
        current_user: User,
    ) -> list[DashboardRecentTransaction]:

        transactions = (
            db.query(
                Transaction,
                Account.name.label("account_name"),
                Account.icon.label("account_icon"),
                Category.name.label("category_name"),
                Category.icon.label("category_icon"),
                Category.color.label("category_color"),
            )
            .join(
                Account,
                Transaction.account_id == Account.id,
            )
            .join(
                Category,
                Transaction.category_id == Category.id,
            )
            .filter(
                Transaction.user_id == current_user.id,
            )
            .order_by(
                Transaction.transaction_date.desc(),
            )
            .limit(10)
            .all()
        )

        return [
            DashboardRecentTransaction(
                id=transaction.id,
                merchant=transaction.merchant,
                description=transaction.description,
                amount=transaction.amount,
                transaction_date=transaction.transaction_date,
                category_name=category_name,
                category_icon=category_icon,
                category_color=category_color,
                account_name=account_name,
                account_icon=account_icon,
            )
            for (
                transaction,
                account_name,
                account_icon,
                category_name,
                category_icon,
                category_color,
            ) in transactions
        ]
