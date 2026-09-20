from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.session import get_db
from app.dependencies.services import get_savings_allocation_service
from app.models.user import User
from app.schemas.savings_allocation import (
    SavingsAllocationCreate,
    SavingsAllocationResponse,
    SavingsAllocationSummaryResponse,
    SavingsAllocationUpdate,
)
from app.services.savings_allocation_service import SavingsAllocationService

router = APIRouter(
    prefix="/savings-allocations",
    tags=["Savings Allocations"],
)


@router.post(
    "",
    response_model=SavingsAllocationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_savings_allocation(
    allocation: SavingsAllocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: SavingsAllocationService = Depends(get_savings_allocation_service),
):
    try:
        return service.create_allocation(
            db,
            current_user,
            allocation,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=list[SavingsAllocationResponse],
)
def get_savings_allocations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: SavingsAllocationService = Depends(get_savings_allocation_service),
):
    return service.get_allocations(
        db,
        current_user,
    )


@router.get(
    "/summary",
    response_model=SavingsAllocationSummaryResponse,
)
def get_savings_allocation_summary(
    month: int = Query(
        ge=1,
        le=12,
    ),
    year: int = Query(
        ge=2000,
        le=2100,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: SavingsAllocationService = Depends(get_savings_allocation_service),
):
    return service.get_monthly_summary(
        db,
        current_user,
        month,
        year,
    )


@router.get(
    "/{allocation_id}",
    response_model=SavingsAllocationResponse,
)
def get_savings_allocation(
    allocation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: SavingsAllocationService = Depends(get_savings_allocation_service),
):
    allocation = service.get_allocation(
        db,
        allocation_id,
        current_user,
    )

    if allocation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Savings allocation not found",
        )

    return allocation


@router.patch(
    "/{allocation_id}",
    response_model=SavingsAllocationResponse,
)
def update_savings_allocation(
    allocation_id: int,
    allocation: SavingsAllocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: SavingsAllocationService = Depends(get_savings_allocation_service),
):
    try:
        updated = service.update_allocation(
            db,
            allocation_id,
            current_user,
            allocation,
        )

        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Savings allocation not found",
            )

        return updated

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.delete(
    "/{allocation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_savings_allocation(
    allocation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: SavingsAllocationService = Depends(get_savings_allocation_service),
):
    deleted = service.delete_allocation(
        db,
        allocation_id,
        current_user,
    )

    if deleted is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Savings allocation not found",
        )
