from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.enums.category import CategoryType
from app.models.category import Category
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
    def get_income_total_for_account(
        self,
        db: Session,
        account_id: int,
        user_id: int,
    ):
        return (
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
                Transaction.account_id == account_id,
                Transaction.user_id == user_id,
                Category.type == CategoryType.INCOME,
                Transaction.transaction_date <= func.now(),
            )
            .scalar()
        )

    def get_expense_total_for_account(
        self,
        db: Session,
        account_id: int,
        user_id: int,
    ):
        return (
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
                Transaction.account_id == account_id,
                Transaction.user_id == user_id,
                Category.type == CategoryType.EXPENSE,
                Transaction.transaction_date <= func.now(),
            )
            .scalar()
        )