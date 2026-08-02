from decimal import Decimal

from sqlalchemy.orm import Session

from app.enums.category import CategoryType
from app.models.budget import Budget
from app.models.category import Category
from app.models.user import User
from app.repositories.budget_repository import BudgetRepository
from app.repositories.category_repository import CategoryRepository
from app.schemas.budget import (
    BudgetCreate,
    BudgetUpdate,
)


class BudgetService:

    def __init__(self):
        self.repository = BudgetRepository()
        self.category_repository = CategoryRepository()

    def create_budget(
        self,
        db: Session,
        current_user: User,
        budget_data: BudgetCreate,
    ) -> Budget:

        self._validate_amount(
            budget_data.amount,
        )

        self._get_expense_category(
            db,
            current_user.id,
            budget_data.category_id,
        )

        self._ensure_budget_does_not_exist(
            db,
            current_user.id,
            budget_data.category_id,
            budget_data.month,
            budget_data.year,
        )

        budget = Budget(
            user_id=current_user.id,
            category_id=budget_data.category_id,
            month=budget_data.month,
            year=budget_data.year,
            amount=budget_data.amount,
        )

        return self.repository.save(
            db,
            budget,
        )

    def get_budgets(
        self,
        db: Session,
        current_user: User,
    ) -> list[Budget]:
        return self.repository.get_all(
            db,
            current_user.id,
        )

    def get_budget(
        self,
        db: Session,
        budget_id: int,
        current_user: User,
    ) -> Budget | None:
        return self.repository.get_by_id(
            db,
            budget_id,
            current_user.id,
        )

    def update_budget(
        self,
        db: Session,
        budget_id: int,
        current_user: User,
        budget_data: BudgetUpdate,
    ) -> Budget | None:

        budget = self.repository.get_by_id(
            db,
            budget_id,
            current_user.id,
        )

        if budget is None:
            return None

        self._validate_amount(
            budget_data.amount,
        )

        self._get_expense_category(
            db,
            current_user.id,
            budget_data.category_id,
        )

        self._ensure_budget_does_not_exist(
            db,
            current_user.id,
            budget_data.category_id,
            budget_data.month,
            budget_data.year,
            budget.id,
        )

        budget.category_id = budget_data.category_id
        budget.month = budget_data.month
        budget.year = budget_data.year
        budget.amount = budget_data.amount

        return self.repository.save(
            db,
            budget,
        )

    def delete_budget(
        self,
        db: Session,
        budget_id: int,
        current_user: User,
    ) -> Budget | None:

        budget = self.repository.get_by_id(
            db,
            budget_id,
            current_user.id,
        )

        if budget is None:
            return None

        self.repository.delete(
            db,
            budget,
        )

        return budget

    def _validate_amount(
        self,
        amount: Decimal,
    ) -> None:
        if amount <= 0:
            raise ValueError(
                "Budget amount must be greater than zero."
            )

    def _get_expense_category(
        self,
        db: Session,
        user_id: int,
        category_id: int,
    ) -> Category:
        category = self.category_repository.get_by_id(
            db,
            category_id,
            user_id,
        )

        if category is None:
            raise ValueError(
                "Category not found."
            )

        if category.type != CategoryType.EXPENSE:
            raise ValueError(
                "Budgets are allowed only for expense categories."
            )

        return category

    def _ensure_budget_does_not_exist(
        self,
        db: Session,
        user_id: int,
        category_id: int,
        month: int,
        year: int,
        budget_id: int | None = None,
    ) -> None:
        existing = self.repository.get_existing_budget(
            db,
            user_id,
            category_id,
            month,
            year,
        )

        if existing is not None and existing.id != budget_id:
            raise ValueError("Budget already exists.")
