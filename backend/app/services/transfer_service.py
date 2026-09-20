from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.transfer import Transfer
from app.repositories.transfer_repository import TransferRepository
from app.schemas.transfer import TransferCreate


class TransferService:

    def __init__(self):
        self.repository = TransferRepository()

    def create_transfer(
        self,
        db: Session,
        current_user,
        data: TransferCreate,
    ) -> Transfer:

        # 1. Source and destination cannot be the same
        if data.source_account_id == data.destination_account_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Source and destination accounts must be different.",
            )

        # 2. Amount must be positive
        if data.amount <= Decimal("0"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transfer amount must be greater than zero.",
            )

        # 3. Get source account
        source_account = (
            db.query(Account)
            .filter(
                Account.id == data.source_account_id,
                Account.user_id == current_user.id,
            )
            .first()
        )

        if source_account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source account not found.",
            )

        # 4. Get destination account
        destination_account = (
            db.query(Account)
            .filter(
                Account.id == data.destination_account_id,
                Account.user_id == current_user.id,
            )
            .first()
        )

        if destination_account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Destination account not found.",
            )

        # 5. Currency must match for now
        if source_account.currency != destination_account.currency:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transfers between different currencies are not supported yet.",
            )

        # 6. Create transfer
        transfer = Transfer(
            user_id=current_user.id,
            source_account_id=data.source_account_id,
            destination_account_id=data.destination_account_id,
            amount=data.amount,
            description=data.description,
            transfer_date=data.transfer_date,
        )

        # 7. Persist transfer
        self.repository.create(
            db=db,
            transfer=transfer,
        )

        return transfer

    def get_transfer(
        self,
        db: Session,
        current_user,
        transfer_id: int,
    ) -> Transfer:

        transfer = self.repository.get_by_id(
            db=db,
            transfer_id=transfer_id,
            user_id=current_user.id,
        )

        if transfer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transfer not found.",
            )

        return transfer

    def get_transfers(
        self,
        db: Session,
        current_user,
    ) -> list[Transfer]:

        return self.repository.get_all(
            db=db,
            user_id=current_user.id,
        )

    def delete_transfer(
        self,
        db: Session,
        current_user,
        transfer_id: int,
    ) -> None:

        transfer = self.repository.get_by_id(
            db=db,
            transfer_id=transfer_id,
            user_id=current_user.id,
        )

        if transfer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transfer not found.",
            )

        self.repository.delete(
            db=db,
            transfer=transfer,
        )