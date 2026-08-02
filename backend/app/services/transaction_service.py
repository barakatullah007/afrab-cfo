from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.transaction import TransactionCreate


class TransactionService:

    def __init__(self):
        self.repository = TransactionRepository()

    def create_transaction(
        self,
        db: Session,
        transaction_data: TransactionCreate,
    ) -> Transaction:

        transaction = Transaction(
            description=transaction_data.description,
            amount=transaction_data.amount,
        )

        return self.repository.create(db, transaction)

    def get_transactions(
        self,
        db: Session,
    ):
        return self.repository.get_all(db)

    def get_transaction(
        self,
        db: Session,
        transaction_id: int,
    ):
        return self.repository.get_by_id(
            db,
            transaction_id,
        )

    def delete_transaction(
        self,
        db: Session,
        transaction_id: int,
    ):
        transaction = self.repository.get_by_id(
            db,
            transaction_id,
        )

        if transaction is None:
            return None

        self.repository.delete(
            db,
            transaction,
        )

        return transaction