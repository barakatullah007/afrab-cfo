from decimal import Decimal

from sqlalchemy.orm import Session

from app.enums.goal import GoalStatus
from app.models.goal import Goal
from app.models.user import User
from app.repositories.goal_repository import GoalRepository
from app.schemas.goal import (
    GoalCreate,
    GoalUpdate,
)


class GoalService:

    def __init__(self):
        self.repository = GoalRepository()

    def create_goal(
        self,
        db: Session,
        current_user: User,
        goal_data: GoalCreate,
    ) -> Goal:

        status = self._resolve_status(
            goal_data.current_amount,
            goal_data.target_amount,
            goal_data.status,
        )

        goal = Goal(
            user_id=current_user.id,
            name=goal_data.name,
            description=goal_data.description,
            target_amount=goal_data.target_amount,
            current_amount=goal_data.current_amount,
            target_date=goal_data.target_date,
            priority=goal_data.priority,
            status=status,
        )

        return self.repository.create(
            db,
            goal,
        )

    def get_goals(
        self,
        db: Session,
        current_user: User,
    ) -> list[Goal]:
        return self.repository.get_all(
            db,
            current_user.id,
        )

    def get_goal(
        self,
        db: Session,
        goal_id: int,
        current_user: User,
    ) -> Goal | None:
        return self.repository.get_by_id(
            db,
            goal_id,
            current_user.id,
        )

    def update_goal(
        self,
        db: Session,
        goal_id: int,
        current_user: User,
        goal_data: GoalUpdate,
    ) -> Goal | None:

        goal = self.repository.get_by_id(
            db,
            goal_id,
            current_user.id,
        )

        if goal is None:
            return None

        if goal.status == GoalStatus.CANCELLED:
            raise ValueError(
                "Cancelled goals cannot be updated."
            )

        status = self._resolve_status(
            goal_data.current_amount,
            goal_data.target_amount,
            goal_data.status,
        )

        goal.name = goal_data.name
        goal.description = goal_data.description
        goal.target_amount = goal_data.target_amount
        goal.current_amount = goal_data.current_amount
        goal.target_date = goal_data.target_date
        goal.priority = goal_data.priority
        goal.status = status

        return self.repository.save(
            db,
            goal,
        )

    def delete_goal(
        self,
        db: Session,
        goal_id: int,
        current_user: User,
    ) -> Goal | None:

        goal = self.repository.get_by_id(
            db,
            goal_id,
            current_user.id,
        )

        if goal is None:
            return None

        self.repository.delete(
            db,
            goal,
        )

        return goal

    def _resolve_status(
        self,
        current_amount: Decimal,
        target_amount: Decimal,
        requested_status: GoalStatus,
    ) -> GoalStatus:
        if current_amount > target_amount:
            raise ValueError(
                "Current amount cannot exceed target amount."
            )

        if current_amount == target_amount:
            return GoalStatus.COMPLETED

        if requested_status == GoalStatus.COMPLETED:
            raise ValueError(
                "Goal cannot be completed until current amount equals target amount."
            )

        return requested_status
