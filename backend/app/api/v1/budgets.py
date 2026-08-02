from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.session import get_db
from app.dependencies.services import get_budget_service
from app.models.user import User
from app.schemas.budget import (
    BudgetCreate,
    BudgetResponse,
    BudgetUpdate,
)
from app.services.budget_service import BudgetService

router = APIRouter(
    prefix="/budgets",
    tags=["Budgets"],
)


@router.post(
    "",
    response_model=BudgetResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_budget(
    budget: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: BudgetService = Depends(get_budget_service),
):
    try:
        return service.create_budget(
            db,
            current_user,
            budget,
        )
    except ValueError as exc:
        raise _budget_http_exception(exc)


@router.get(
    "",
    response_model=list[BudgetResponse],
)
def get_budgets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: BudgetService = Depends(get_budget_service),
):
    return service.get_budgets(
        db,
        current_user,
    )


@router.get(
    "/{budget_id}",
    response_model=BudgetResponse,
)
def get_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: BudgetService = Depends(get_budget_service),
):
    budget = service.get_budget(
        db,
        budget_id,
        current_user,
    )

    if budget is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found",
        )

    return budget


@router.put(
    "/{budget_id}",
    response_model=BudgetResponse,
)
def update_budget(
    budget_id: int,
    budget: BudgetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: BudgetService = Depends(get_budget_service),
):
    try:
        updated = service.update_budget(
            db,
            budget_id,
            current_user,
            budget,
        )

        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Budget not found",
            )

        return updated

    except ValueError as exc:
        raise _budget_http_exception(exc)


@router.delete(
    "/{budget_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: BudgetService = Depends(get_budget_service),
):
    deleted = service.delete_budget(
        db,
        budget_id,
        current_user,
    )

    if deleted is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found",
        )


def _budget_http_exception(
    exc: ValueError,
) -> HTTPException:
    if str(exc) == "Budget already exists.":
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(exc),
    )
