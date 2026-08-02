from sqlalchemy.orm import Session

from app.models.budget import Budget


class BudgetRepository:

    def save(
        self,
        db: Session,
        budget: Budget,
    ) -> Budget:
        db.add(budget)
        db.commit()
        db.refresh(budget)
        return budget

    def get_all(
        self,
        db: Session,
        user_id: int,
    ) -> list[Budget]:
        return (
            db.query(Budget)
            .filter(Budget.user_id == user_id)
            .order_by(
                Budget.year.desc(),
                Budget.month.desc(),
                Budget.category_id.asc(),
            )
            .all()
        )

    def get_by_id(
        self,
        db: Session,
        budget_id: int,
        user_id: int,
    ) -> Budget | None:
        return (
            db.query(Budget)
            .filter(
                Budget.id == budget_id,
                Budget.user_id == user_id,
            )
            .first()
        )

    def get_existing_budget(
        self,
        db: Session,
        user_id: int,
        category_id: int,
        month: int,
        year: int,
    ) -> Budget | None:
        return (
            db.query(Budget)
            .filter(
                Budget.user_id == user_id,
                Budget.category_id == category_id,
                Budget.month == month,
                Budget.year == year,
            )
            .first()
        )

    def delete(
        self,
        db: Session,
        budget: Budget,
    ) -> None:
        db.delete(budget)
        db.commit()
