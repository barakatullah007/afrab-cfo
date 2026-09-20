from decimal import Decimal

from sqlalchemy.orm import Session

from app.repositories.account_repository import AccountRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.transfer_repository import TransferRepository

class AccountBalanceService:

    def __init__(self):
        self.account_repository = AccountRepository()
        self.transaction_repository = TransactionRepository()
        self.transfer_repository = TransferRepository()
    def get_account_balance(
        self,
        db: Session,
        account_id: int,
        user_id: int,
    ) -> Decimal | None:

        account = self.account_repository.get_by_id(
            db,
            account_id,
            user_id,
        )

        if account is None:
            return None

        income = self.transaction_repository.get_income_total_for_account(
            db,
            account_id,
            user_id,
        )

        expense = self.transaction_repository.get_expense_total_for_account(
            db,
            account_id,
            user_id,
        )
        transfers_out = self.transfer_repository.get_outgoing_total_for_account(
            db,
            account_id,
            user_id,
        )

        transfers_in = self.transfer_repository.get_incoming_total_for_account(
            db,
            account_id,
            user_id,
        )
        opening_balance = account.opening_balance or Decimal("0")
        income = income or Decimal("0")
        expense = expense or Decimal("0")
        transfers_out = transfers_out or Decimal("0")
        transfers_in = transfers_in or Decimal("0")
        return (
            opening_balance
            + Decimal(str(income))
            - Decimal(str(expense))
            - Decimal(str(transfers_out))
            + Decimal(str(transfers_in))
        )

    def get_total_balance(
        self,
        db: Session,
        user_id: int,
    ) -> Decimal:

        accounts = self.account_repository.get_all(
            db,
            user_id,
        )

        total_balance = Decimal("0")

        for account in accounts:

            balance = self.get_account_balance(
                db,
                account.id,
                user_id,
            )

            if balance is not None:
                total_balance += balance

        return total_balance