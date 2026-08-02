from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.session import get_db
from app.dependencies.services import get_goal_service
from app.models.user import User
from app.schemas.goal import (
    GoalCreate,
    GoalResponse,
    GoalUpdate,
)
from app.services.goal_service import GoalService

router = APIRouter(
    prefix="/goals",
    tags=["Goals"],
)


@router.post(
    "",
    response_model=GoalResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_goal(
    goal: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: GoalService = Depends(get_goal_service),
):
    try:
        return service.create_goal(
            db,
            current_user,
            goal,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=list[GoalResponse],
)
def get_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: GoalService = Depends(get_goal_service),
):
    return service.get_goals(
        db,
        current_user,
    )


@router.get(
    "/{goal_id}",
    response_model=GoalResponse,
)
def get_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: GoalService = Depends(get_goal_service),
):
    goal = service.get_goal(
        db,
        goal_id,
        current_user,
    )

    if goal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )

    return goal


@router.put(
    "/{goal_id}",
    response_model=GoalResponse,
)
def update_goal(
    goal_id: int,
    goal: GoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: GoalService = Depends(get_goal_service),
):
    try:
        updated = service.update_goal(
            db,
            goal_id,
            current_user,
            goal,
        )

        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goal not found",
            )

        return updated

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.delete(
    "/{goal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: GoalService = Depends(get_goal_service),
):
    deleted = service.delete_goal(
        db,
        goal_id,
        current_user,
    )

    if deleted is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found",
        )
