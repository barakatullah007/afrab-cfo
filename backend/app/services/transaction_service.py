from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.models.user import User
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
)


class TransactionService:

    def __init__(self):
        self.repository = TransactionRepository()

    def create_transaction(
        self,
        db: Session,
        current_user: User,
        transaction_data: TransactionCreate,
    ) -> Transaction:

        transaction = Transaction(
            user_id=current_user.id,
            account_id=transaction_data.account_id,
            category_id=transaction_data.category_id,
            description=transaction_data.description,
            merchant=transaction_data.merchant,
            amount=transaction_data.amount,
            notes=transaction_data.notes,
            transaction_date=transaction_data.transaction_date,
        )

        return self.repository.save(
            db,
            transaction,
        )

    def get_transactions(
        self,
        db: Session,
        current_user: User,
    ) -> list[Transaction]:
        return self.repository.get_all(
            db,
            current_user.id,
        )

    def get_transaction(
        self,
        db: Session,
        transaction_id: int,
        current_user: User,
    ) -> Transaction | None:
        return self.repository.get_by_id(
            db,
            transaction_id,
            current_user.id,
        )

    def update_transaction(
        self,
        db: Session,
        transaction_id: int,
        current_user: User,
        transaction_data: TransactionUpdate,
    ) -> Transaction | None:

        transaction = self.repository.get_by_id(
            db,
            transaction_id,
            current_user.id,
        )

        if transaction is None:
            return None

        transaction.account_id = transaction_data.account_id
        transaction.category_id = transaction_data.category_id
        transaction.description = transaction_data.description
        transaction.merchant = transaction_data.merchant
        transaction.amount = transaction_data.amount
        transaction.notes = transaction_data.notes
        transaction.transaction_date = transaction_data.transaction_date

        return self.repository.save(
            db,
            transaction,
        )

    def delete_transaction(
        self,
        db: Session,
        transaction_id: int,
        current_user: User,
    ) -> Transaction | None:

        transaction = self.repository.get_by_id(
            db,
            transaction_id,
            current_user.id,
        )

        if transaction is None:
            return None

        self.repository.delete(
            db,
            transaction,
        )

        return transaction