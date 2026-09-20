from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.transfer import (
    TransferCreate,
    TransferResponse,
)
from app.services.transfer_service import TransferService


router = APIRouter(
    prefix="/transfers",
    tags=["Transfers"],
)

service = TransferService()


@router.post(
    "",
    response_model=TransferResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transfer(
    data: TransferCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transfer = service.create_transfer(
        db=db,
        current_user=current_user,
        data=data,
    )

    db.commit()
    db.refresh(transfer)

    return transfer


@router.get(
    "",
    response_model=list[TransferResponse],
)
def get_transfers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.get_transfers(
        db=db,
        current_user=current_user,
    )


@router.get(
    "/{transfer_id}",
    response_model=TransferResponse,
)
def get_transfer(
    transfer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.get_transfer(
        db=db,
        current_user=current_user,
        transfer_id=transfer_id,
    )


@router.delete(
    "/{transfer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_transfer(
    transfer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service.delete_transfer(
        db=db,
        current_user=current_user,
        transfer_id=transfer_id,
    )

    db.commit()