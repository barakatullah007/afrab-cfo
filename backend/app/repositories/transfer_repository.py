from sqlalchemy.orm import Session

from app.models.transfer import Transfer

from sqlalchemy import func
class TransferRepository:

    def create(
        self,
        db: Session,
        transfer: Transfer,
    ) -> Transfer:
        db.add(transfer)
        db.flush()

        return transfer

    def get_by_id(
        self,
        db: Session,
        transfer_id: int,
        user_id: int,
    ) -> Transfer | None:

        return (
            db.query(Transfer)
            .filter(
                Transfer.id == transfer_id,
                Transfer.user_id == user_id,
            )
            .first()
        )

    def get_all(
        self,
        db: Session,
        user_id: int,
    ) -> list[Transfer]:

        return (
            db.query(Transfer)
            .filter(
                Transfer.user_id == user_id,
            )
            .order_by(
                Transfer.transfer_date.desc(),
            )
            .all()
        )

    def delete(
        self,
        db: Session,
        transfer: Transfer,
    ) -> None:

        db.delete(transfer)
        db.flush()
        
    def get_outgoing_total_for_account(
        self,
        db: Session,
        account_id: int,
        user_id: int,
    ):
        return (
            db.query(func.coalesce(func.sum(Transfer.amount), 0))
            .filter(
                Transfer.source_account_id == account_id,
                Transfer.user_id == user_id,
                Transfer.transfer_date <= func.now(),
            )
            .scalar()
        )
        
    def get_incoming_total_for_account(
        self,
        db: Session,
        account_id: int,
        user_id: int,
    ):
        return (
            db.query(func.coalesce(func.sum(Transfer.amount), 0))
            .filter(
                Transfer.destination_account_id == account_id,
                Transfer.user_id == user_id,
                Transfer.transfer_date <= func.now(),
            )
            .scalar()
        )