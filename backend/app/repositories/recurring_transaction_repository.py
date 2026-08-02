from datetime import datetime

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.recurring_transaction import RecurringTransaction


class RecurringTransactionRepository:

    def save(
        self,
        db: Session,
        recurring_transaction: RecurringTransaction,
    ) -> RecurringTransaction:
        db.add(recurring_transaction)
        db.commit()
        db.refresh(recurring_transaction)
        return recurring_transaction

    def delete(
        self,
        db: Session,
        recurring_transaction: RecurringTransaction,
    ) -> None:
        db.delete(recurring_transaction)
        db.commit()

    def get_by_id(
        self,
        db: Session,
        recurring_transaction_id: int,
        user_id: int,
    ) -> RecurringTransaction | None:
        return (
            db.query(RecurringTransaction)
            .filter(
                RecurringTransaction.id == recurring_transaction_id,
                RecurringTransaction.user_id == user_id,
            )
            .first()
        )

    def get_all(
        self,
        db: Session,
        user_id: int,
    ) -> list[RecurringTransaction]:
        return (
            db.query(RecurringTransaction)
            .filter(RecurringTransaction.user_id == user_id)
            .order_by(
                RecurringTransaction.next_run_date.asc(),
            )
            .all()
        )

    def get_due_transactions(
        self,
        db: Session,
        due_at: datetime,
    ) -> list[RecurringTransaction]:
        return (
            db.query(RecurringTransaction)
            .filter(
                RecurringTransaction.is_active.is_(True),
                RecurringTransaction.next_run_date <= due_at,
                or_(
                    RecurringTransaction.end_date.is_(None),
                    RecurringTransaction.end_date >= due_at,
                ),
            )
            .order_by(
                RecurringTransaction.next_run_date.asc(),
            )
            .all()
        )
