from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.enums.category import CategoryType
from app.enums.goal import GoalStatus
from app.models.account import Account
from app.models.budget import Budget
from app.models.category import Category
from app.models.goal import Goal
from app.models.recurring_transaction import RecurringTransaction
from app.models.transaction import Transaction
from app.models.user import User
from app.repositories.budget_repository import BudgetRepository
from app.repositories.goal_repository import GoalRepository
from app.schemas.financial_intelligence import (
    BudgetUtilizationInsight,
    CategoryInsight,
    FinancialIntelligenceSummary,
    GoalProgressInsight,
    MonthlyCashFlow,
)


class FinancialIntelligenceService:

    def __init__(self):
        self.budget_repository = BudgetRepository()
        self.goal_repository = GoalRepository()

    def get_summary(
        self,
        db: Session,
        current_user: User,
    ) -> FinancialIntelligenceSummary:
        monthly_income, monthly_expense = self._get_monthly_totals(
            db,
            current_user.id,
        )

        monthly_cash_flow = monthly_income - monthly_expense

        return FinancialIntelligenceSummary(
            net_worth=self._get_net_worth(
                db,
                current_user.id,
            ),
            monthly_income=monthly_income,
            monthly_expense=monthly_expense,
            monthly_cash_flow=monthly_cash_flow,
            savings_rate=self._get_percentage(
                monthly_cash_flow,
                monthly_income,
            ),
            active_goals=self._count_goals(
                db,
                current_user.id,
                GoalStatus.ACTIVE,
            ),
            completed_goals=self._count_goals(
                db,
                current_user.id,
                GoalStatus.COMPLETED,
            ),
            active_budgets=self._count_current_month_budgets(
                db,
                current_user.id,
            ),
            active_recurring_transactions=self._count_active_recurring_transactions(
                db,
                current_user.id,
            ),
        )

    def get_budget_utilization(
        self,
        db: Session,
        current_user: User,
    ) -> list[BudgetUtilizationInsight]:
        month_start, month_end = self._get_current_month_range()

        rows = (
            db.query(
                Budget,
                Category.name.label("category_name"),
                func.coalesce(
                    func.sum(Transaction.amount),
                    0,
                ).label("spent_amount"),
            )
            .join(
                Category,
                Budget.category_id == Category.id,
            )
            .outerjoin(
                Transaction,
                (Transaction.category_id == Budget.category_id)
                & (Transaction.user_id == Budget.user_id)
                & (Transaction.transaction_date >= month_start)
                & (Transaction.transaction_date < month_end),
            )
            .filter(
                Budget.user_id == current_user.id,
                Budget.month == month_start.month,
                Budget.year == month_start.year,
            )
            .group_by(
                Budget.id,
                Category.name,
            )
            .order_by(
                Category.name.asc(),
            )
            .all()
        )

        return [
            BudgetUtilizationInsight(
                budget_id=budget.id,
                category_id=budget.category_id,
                category_name=category_name,
                budget_amount=budget.amount,
                spent_amount=Decimal(spent_amount),
                remaining_amount=budget.amount - Decimal(spent_amount),
                utilization_percentage=self._get_percentage(
                    Decimal(spent_amount),
                    budget.amount,
                ),
            )
            for (
                budget,
                category_name,
                spent_amount,
            ) in rows
        ]

    def get_goal_progress(
        self,
        db: Session,
        current_user: User,
    ) -> list[GoalProgressInsight]:
        goals = self.goal_repository.get_all(
            db,
            current_user.id,
        )

        return [
            GoalProgressInsight(
                goal_id=goal.id,
                name=goal.name,
                target_amount=goal.target_amount,
                current_amount=goal.current_amount,
                remaining_amount=goal.target_amount - goal.current_amount,
                progress_percentage=self._get_percentage(
                    goal.current_amount,
                    goal.target_amount,
                ),
                status=goal.status,
            )
            for goal in goals
        ]

    def get_category_insights(
        self,
        db: Session,
        current_user: User,
    ) -> list[CategoryInsight]:
        month_start, month_end = self._get_current_month_range()

        rows = (
            db.query(
                Category.id.label("category_id"),
                Category.name.label("category_name"),
                func.coalesce(
                    func.sum(Transaction.amount),
                    0,
                ).label("monthly_spent"),
                func.count(Transaction.id).label("transaction_count"),
            )
            .join(
                Transaction,
                Transaction.category_id == Category.id,
            )
            .filter(
                Transaction.user_id == current_user.id,
                Category.user_id == current_user.id,
                Category.type == CategoryType.EXPENSE,
                Transaction.transaction_date >= month_start,
                Transaction.transaction_date < month_end,
            )
            .group_by(
                Category.id,
                Category.name,
            )
            .order_by(
                func.sum(Transaction.amount).desc(),
            )
            .all()
        )

        return [
            CategoryInsight(
                category_id=category_id,
                category_name=category_name,
                monthly_spent=Decimal(monthly_spent),
                transaction_count=transaction_count,
            )
            for (
                category_id,
                category_name,
                monthly_spent,
                transaction_count,
            ) in rows
        ]

    def get_monthly_cashflow(
        self,
        db: Session,
        current_user: User,
    ) -> MonthlyCashFlow:
        monthly_income, monthly_expense = self._get_monthly_totals(
            db,
            current_user.id,
        )

        return MonthlyCashFlow(
            income=monthly_income,
            expense=monthly_expense,
            cash_flow=monthly_income - monthly_expense,
        )

    def _get_net_worth(
        self,
        db: Session,
        user_id: int,
    ) -> Decimal:
        net_worth = (
            db.query(
                func.coalesce(
                    func.sum(Account.opening_balance),
                    0,
                )
            )
            .filter(Account.user_id == user_id)
            .scalar()
        )

        return Decimal(net_worth)

    def _get_monthly_totals(
        self,
        db: Session,
        user_id: int,
    ) -> tuple[Decimal, Decimal]:
        month_start, _ = self._get_current_month_range()

        return self.get_monthly_totals_for_month(
            db,
            user_id,
            month_start.month,
            month_start.year,
        )

    def get_monthly_totals_for_month(
        self,
        db: Session,
        user_id: int,
        month: int,
        year: int,
    ) -> tuple[Decimal, Decimal]:
        month_start, month_end = self._get_month_range(
            month,
            year,
        )

        rows = (
            db.query(
                Category.type,
                func.coalesce(
                    func.sum(Transaction.amount),
                    0,
                ),
            )
            .join(
                Category,
                Transaction.category_id == Category.id,
            )
            .filter(
                Transaction.user_id == user_id,
                Category.user_id == user_id,
                Transaction.transaction_date >= month_start,
                Transaction.transaction_date < month_end,
            )
            .group_by(Category.type)
            .all()
        )

        totals = {
            category_type: Decimal(amount)
            for (
                category_type,
                amount,
            ) in rows
        }

        return (
            totals.get(
                CategoryType.INCOME,
                Decimal("0"),
            ),
            totals.get(
                CategoryType.EXPENSE,
                Decimal("0"),
            ),
        )

    def _get_month_range(
        self,
        month: int,
        year: int,
    ) -> tuple[datetime, datetime]:
        month_start = datetime(
            year,
            month,
            1,
            tzinfo=UTC,
        )

        if month == 12:
            next_month_start = datetime(
                year + 1,
                1,
                1,
                tzinfo=UTC,
            )
        else:
            next_month_start = datetime(
                year,
                month + 1,
                1,
                tzinfo=UTC,
            )

        return (
            month_start,
            next_month_start,
        )

    def _count_goals(
        self,
        db: Session,
        user_id: int,
        status: GoalStatus,
    ) -> int:
        return (
            db.query(Goal)
            .filter(
                Goal.user_id == user_id,
                Goal.status == status,
            )
            .count()
        )

    def _count_current_month_budgets(
        self,
        db: Session,
        user_id: int,
    ) -> int:
        month_start, _ = self._get_current_month_range()

        return (
            db.query(Budget)
            .filter(
                Budget.user_id == user_id,
                Budget.month == month_start.month,
                Budget.year == month_start.year,
            )
            .count()
        )

    def _count_active_recurring_transactions(
        self,
        db: Session,
        user_id: int,
    ) -> int:
        return (
            db.query(RecurringTransaction)
            .filter(
                RecurringTransaction.user_id == user_id,
                RecurringTransaction.is_active.is_(True),
            )
            .count()
        )

    def _get_current_month_range(self) -> tuple[datetime, datetime]:
        now = datetime.now(UTC)

        return self._get_month_range(
            now.month,
            now.year,
        )

    def _get_percentage(
        self,
        numerator: Decimal,
        denominator: Decimal,
    ) -> Decimal:
        if denominator == 0:
            return Decimal("0")

        return (numerator / denominator) * Decimal("100")
