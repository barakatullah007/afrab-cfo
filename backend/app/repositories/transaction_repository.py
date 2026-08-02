from sqlalchemy.orm import Session

from app.models.transaction import Transaction


class TransactionRepository:

    def create(
        self,
        db: Session,
        transaction: Transaction,
    ) -> Transaction:
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction

    def get_all(
        self,
        db: Session,
    ):
        return db.query(Transaction).all()

    def get_by_id(
        self,
        db: Session,
        transaction_id: int,
    ):
        return (
            db.query(Transaction)
            .filter(Transaction.id == transaction_id)
            .first()
        )

    def delete(
        self,
        db: Session,
        transaction: Transaction,
    ):
        db.delete(transaction)
        db.commit()