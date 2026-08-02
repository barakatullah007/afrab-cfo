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
            description=transaction_data.description,
            amount=transaction_data.amount,
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

        transaction.description = transaction_data.description
        transaction.amount = transaction_data.amount

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