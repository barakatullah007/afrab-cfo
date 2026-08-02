from sqlalchemy.orm import Session

from app.models.transaction import Transaction


class TransactionRepository:

    def save(
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
        user_id: int,
    ) -> list[Transaction]:
        return (
            db.query(Transaction)
            .filter(
                Transaction.user_id == user_id,
            )
            .order_by(
                Transaction.transaction_date.desc(),
            )
            .all()
        )

    def get_by_id(
        self,
        db: Session,
        transaction_id: int,
        user_id: int,
    ) -> Transaction | None:
        return (
            db.query(Transaction)
            .filter(
                Transaction.id == transaction_id,
                Transaction.user_id == user_id,
            )
            .first()
        )

    def delete(
        self,
        db: Session,
        transaction: Transaction,
    ) -> None:
        db.delete(transaction)
        db.commit()