from sqlalchemy.orm import Session

from app.models.goal import Goal


class GoalRepository:

    def create(
        self,
        db: Session,
        goal: Goal,
    ) -> Goal:
        return self.save(
            db,
            goal,
        )

    def save(
        self,
        db: Session,
        goal: Goal,
    ) -> Goal:
        db.add(goal)
        db.commit()
        db.refresh(goal)
        return goal

    def delete(
        self,
        db: Session,
        goal: Goal,
    ) -> None:
        db.delete(goal)
        db.commit()

    def get_by_id(
        self,
        db: Session,
        goal_id: int,
        user_id: int,
    ) -> Goal | None:
        return (
            db.query(Goal)
            .filter(
                Goal.id == goal_id,
                Goal.user_id == user_id,
            )
            .first()
        )

    def get_all(
        self,
        db: Session,
        user_id: int,
    ) -> list[Goal]:
        return (
            db.query(Goal)
            .filter(Goal.user_id == user_id)
            .order_by(
                Goal.created_at.desc(),
            )
            .all()
        )
