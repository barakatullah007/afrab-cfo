from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.user import User
from app.repositories.account_repository import AccountRepository
from app.schemas.account import (
    AccountCreate,
    AccountUpdate,
)


class AccountService:

    def __init__(self):
        self.repository = AccountRepository()

    def create_account(
        self,
        db: Session,
        current_user: User,
        account_data: AccountCreate,
    ) -> Account:

        existing = self.repository.get_by_name(
            db,
            current_user.id,
            account_data.name,
        )

        if existing:
            raise ValueError(
                "Account already exists."
            )

        account = Account(
            user_id=current_user.id,
            name=account_data.name,
            type=account_data.type,
            opening_balance=account_data.opening_balance,
            currency=account_data.currency,
            icon=account_data.icon,
            color=account_data.color,
            is_default=False,
        )

        return self.repository.save(
            db,
            account,
        )

    def get_accounts(
        self,
        db: Session,
        current_user: User,
    ) -> list[Account]:
        return self.repository.get_all(
            db,
            current_user.id,
        )

    def update_account(
        self,
        db: Session,
        account_id: int,
        current_user: User,
        account_data: AccountUpdate,
    ) -> Account | None:

        account = self.repository.get_by_id(
            db,
            account_id,
            current_user.id,
        )

        if account is None:
            return None

        account.name = account_data.name
        account.type = account_data.type
        account.opening_balance = account_data.opening_balance
        account.currency = account_data.currency
        account.icon = account_data.icon
        account.color = account_data.color

        return self.repository.save(
            db,
            account,
        )

    def delete_account(
        self,
        db: Session,
        account_id: int,
        current_user: User,
    ) -> Account | None:

        account = self.repository.get_by_id(
            db,
            account_id,
            current_user.id,
        )

        if account is None:
            return None

        if account.is_default:
            raise ValueError(
                "Default accounts cannot be deleted."
            )

        self.repository.delete(
            db,
            account,
        )

        return account
