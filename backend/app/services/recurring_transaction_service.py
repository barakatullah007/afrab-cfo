from sqlalchemy.orm import Session

from app.enums.category import CategoryType
from app.enums.recurring_transaction import RecurringTransactionType
from app.models.account import Account
from app.models.category import Category
from app.models.recurring_transaction import RecurringTransaction
from app.models.user import User
from app.repositories.account_repository import AccountRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.recurring_transaction_repository import (
    RecurringTransactionRepository,
)
from app.schemas.recurring_transaction import (
    RecurringTransactionCreate,
    RecurringTransactionUpdate,
)


class RecurringTransactionService:

    def __init__(self):
        self.repository = RecurringTransactionRepository()
        self.account_repository = AccountRepository()
        self.category_repository = CategoryRepository()

    def create_recurring_transaction(
        self,
        db: Session,
        current_user: User,
        recurring_data: RecurringTransactionCreate,
    ) -> RecurringTransaction:

        self._validate_account_and_category(
            db,
            current_user.id,
            recurring_data.account_id,
            recurring_data.category_id,
            recurring_data.transaction_type,
        )

        recurring_transaction = RecurringTransaction(
            user_id=current_user.id,
            account_id=recurring_data.account_id,
            category_id=recurring_data.category_id,
            title=recurring_data.title,
            description=recurring_data.description,
            amount=recurring_data.amount,
            transaction_type=recurring_data.transaction_type,
            frequency=recurring_data.frequency,
            start_date=recurring_data.start_date,
            end_date=recurring_data.end_date,
            next_run_date=recurring_data.next_run_date,
            is_active=True,
        )

        return self.repository.save(
            db,
            recurring_transaction,
        )

    def get_recurring_transactions(
        self,
        db: Session,
        current_user: User,
    ) -> list[RecurringTransaction]:
        return self.repository.get_all(
            db,
            current_user.id,
        )

    def get_recurring_transaction(
        self,
        db: Session,
        recurring_transaction_id: int,
        current_user: User,
    ) -> RecurringTransaction | None:
        return self.repository.get_by_id(
            db,
            recurring_transaction_id,
            current_user.id,
        )

    def update_recurring_transaction(
        self,
        db: Session,
        recurring_transaction_id: int,
        current_user: User,
        recurring_data: RecurringTransactionUpdate,
    ) -> RecurringTransaction | None:

        recurring_transaction = self.repository.get_by_id(
            db,
            recurring_transaction_id,
            current_user.id,
        )

        if recurring_transaction is None:
            return None

        self._validate_account_and_category(
            db,
            current_user.id,
            recurring_data.account_id,
            recurring_data.category_id,
            recurring_data.transaction_type,
        )

        recurring_transaction.account_id = recurring_data.account_id
        recurring_transaction.category_id = recurring_data.category_id
        recurring_transaction.title = recurring_data.title
        recurring_transaction.description = recurring_data.description
        recurring_transaction.amount = recurring_data.amount
        recurring_transaction.transaction_type = recurring_data.transaction_type
        recurring_transaction.frequency = recurring_data.frequency
        recurring_transaction.start_date = recurring_data.start_date
        recurring_transaction.end_date = recurring_data.end_date
        recurring_transaction.next_run_date = recurring_data.next_run_date
        recurring_transaction.is_active = recurring_data.is_active

        return self.repository.save(
            db,
            recurring_transaction,
        )

    def delete_recurring_transaction(
        self,
        db: Session,
        recurring_transaction_id: int,
        current_user: User,
    ) -> RecurringTransaction | None:

        recurring_transaction = self.repository.get_by_id(
            db,
            recurring_transaction_id,
            current_user.id,
        )

        if recurring_transaction is None:
            return None

        self.repository.delete(
            db,
            recurring_transaction,
        )

        return recurring_transaction

    def activate_recurring_transaction(
        self,
        db: Session,
        recurring_transaction_id: int,
        current_user: User,
    ) -> RecurringTransaction | None:

        recurring_transaction = self.repository.get_by_id(
            db,
            recurring_transaction_id,
            current_user.id,
        )

        if recurring_transaction is None:
            return None

        recurring_transaction.is_active = True

        return self.repository.save(
            db,
            recurring_transaction,
        )

    def deactivate_recurring_transaction(
        self,
        db: Session,
        recurring_transaction_id: int,
        current_user: User,
    ) -> RecurringTransaction | None:

        recurring_transaction = self.repository.get_by_id(
            db,
            recurring_transaction_id,
            current_user.id,
        )

        if recurring_transaction is None:
            return None

        recurring_transaction.is_active = False

        return self.repository.save(
            db,
            recurring_transaction,
        )

    def _validate_account_and_category(
        self,
        db: Session,
        user_id: int,
        account_id: int,
        category_id: int,
        transaction_type: RecurringTransactionType,
    ) -> tuple[Account, Category]:

        account = self.account_repository.get_by_id(
            db,
            account_id,
            user_id,
        )

        if account is None:
            raise ValueError(
                "Account not found."
            )

        category = self.category_repository.get_by_id(
            db,
            category_id,
            user_id,
        )

        if category is None:
            raise ValueError(
                "Category not found."
            )

        if (
            transaction_type == RecurringTransactionType.INCOME
            and category.type != CategoryType.INCOME
        ):
            raise ValueError(
                "Income recurring transactions must use income categories."
            )

        if (
            transaction_type == RecurringTransactionType.EXPENSE
            and category.type != CategoryType.EXPENSE
        ):
            raise ValueError(
                "Expense recurring transactions must use expense categories."
            )

        return (
            account,
            category,
        )
