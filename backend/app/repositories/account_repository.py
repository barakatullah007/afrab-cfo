from sqlalchemy.orm import Session

from app.models.account import Account


class AccountRepository:

    def save(
        self,
        db: Session,
        account: Account,
    ) -> Account:
        db.add(account)
        db.commit()
        db.refresh(account)
        return account

    def get_all(
        self,
        db: Session,
        user_id: int,
    ) -> list[Account]:
        return (
            db.query(Account)
            .filter(Account.user_id == user_id)
            .order_by(Account.name.asc())
            .all()
        )

    def get_by_id(
        self,
        db: Session,
        account_id: int,
        user_id: int,
    ) -> Account | None:
        return (
            db.query(Account)
            .filter(
                Account.id == account_id,
                Account.user_id == user_id,
            )
            .first()
        )

    def get_by_name(
        self,
        db: Session,
        user_id: int,
        name: str,
    ) -> Account | None:
        return (
            db.query(Account)
            .filter(
                Account.user_id == user_id,
                Account.name == name,
            )
            .first()
        )

    def delete(
        self,
        db: Session,
        account: Account,
    ) -> None:
        db.delete(account)
        db.commit()