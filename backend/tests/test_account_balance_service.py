from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.services.account_balance_service import AccountBalanceService


def test_account_balance_with_opening_balance(
    db,
    test_user,
    test_account,
):
    service = AccountBalanceService()

    balance = service.get_account_balance(
        db=db,
        account_id=test_account.id,
        user_id=test_user.id,
    )

    assert balance == Decimal("10000.00")


def test_account_balance_includes_income(
    db,
    test_user,
    test_account,
    income_category,
    create_transaction,
):
    create_transaction(
        user_id=test_user.id,
        account_id=test_account.id,
        category_id=income_category.id,
        amount="5000.00",
    )

    service = AccountBalanceService()

    balance = service.get_account_balance(
        db=db,
        account_id=test_account.id,
        user_id=test_user.id,
    )

    assert balance == Decimal("15000.00")


def test_account_balance_subtracts_expense(
    db,
    test_user,
    test_account,
    expense_category,
    create_transaction,
):
    create_transaction(
        user_id=test_user.id,
        account_id=test_account.id,
        category_id=expense_category.id,
        amount="2000.00",
    )

    service = AccountBalanceService()

    balance = service.get_account_balance(
        db=db,
        account_id=test_account.id,
        user_id=test_user.id,
    )

    assert balance == Decimal("8000.00")


def test_account_balance_handles_income_and_expense(
    db,
    test_user,
    test_account,
    income_category,
    expense_category,
    create_transaction,
):
    create_transaction(
        user_id=test_user.id,
        account_id=test_account.id,
        category_id=income_category.id,
        amount="5000.00",
    )

    create_transaction(
        user_id=test_user.id,
        account_id=test_account.id,
        category_id=expense_category.id,
        amount="2000.00",
    )

    service = AccountBalanceService()

    balance = service.get_account_balance(
        db=db,
        account_id=test_account.id,
        user_id=test_user.id,
    )

    assert balance == Decimal("13000.00")


def test_transfer_out_reduces_source_account_balance(
    db,
    test_user,
    test_account,
    test_account_2,
    create_transfer,
):
    create_transfer(
        user_id=test_user.id,
        source_account_id=test_account.id,
        destination_account_id=test_account_2.id,
        amount="3000.00",
    )

    service = AccountBalanceService()

    balance = service.get_account_balance(
        db=db,
        account_id=test_account.id,
        user_id=test_user.id,
    )

    assert balance == Decimal("7000.00")


def test_transfer_in_increases_destination_account_balance(
    db,
    test_user,
    test_account,
    test_account_2,
    create_transfer,
):
    create_transfer(
        user_id=test_user.id,
        source_account_id=test_account.id,
        destination_account_id=test_account_2.id,
        amount="3000.00",
    )

    service = AccountBalanceService()

    balance = service.get_account_balance(
        db=db,
        account_id=test_account_2.id,
        user_id=test_user.id,
    )

    assert balance == Decimal("8000.00")


def test_transfer_does_not_change_total_balance(
    db,
    test_user,
    test_account,
    test_account_2,
    create_transfer,
):
    service = AccountBalanceService()

    before = service.get_total_balance(
        db=db,
        user_id=test_user.id,
    )

    create_transfer(
        user_id=test_user.id,
        source_account_id=test_account.id,
        destination_account_id=test_account_2.id,
        amount="3000.00",
    )

    after = service.get_total_balance(
        db=db,
        user_id=test_user.id,
    )

    assert before == Decimal("15000.00")
    assert after == Decimal("15000.00")


def test_future_transfer_is_ignored(
    db,
    test_user,
    test_account,
    test_account_2,
    create_transfer,
):
    future_date = datetime.now(timezone.utc) + timedelta(days=1)

    create_transfer(
        user_id=test_user.id,
        source_account_id=test_account.id,
        destination_account_id=test_account_2.id,
        amount="3000.00",
        transfer_date=future_date,
    )

    service = AccountBalanceService()

    source_balance = service.get_account_balance(
        db=db,
        account_id=test_account.id,
        user_id=test_user.id,
    )

    destination_balance = service.get_account_balance(
        db=db,
        account_id=test_account_2.id,
        user_id=test_user.id,
    )

    assert source_balance == Decimal("10000.00")
    assert destination_balance == Decimal("5000.00")


def test_current_transfer_is_included(
    db,
    test_user,
    test_account,
    test_account_2,
    create_transfer,
):
    current_date = datetime.now(timezone.utc) - timedelta(minutes=1)

    create_transfer(
        user_id=test_user.id,
        source_account_id=test_account.id,
        destination_account_id=test_account_2.id,
        amount="3000.00",
        transfer_date=current_date,
    )

    service = AccountBalanceService()

    source_balance = service.get_account_balance(
        db=db,
        account_id=test_account.id,
        user_id=test_user.id,
    )

    destination_balance = service.get_account_balance(
        db=db,
        account_id=test_account_2.id,
        user_id=test_user.id,
    )

    assert source_balance == Decimal("7000.00")
    assert destination_balance == Decimal("8000.00")


def test_future_transaction_is_ignored(
    db,
    test_user,
    test_account,
    income_category,
    create_transaction,
):
    future_date = datetime.now(timezone.utc) + timedelta(days=1)

    create_transaction(
        user_id=test_user.id,
        account_id=test_account.id,
        category_id=income_category.id,
        amount="5000.00",
        transaction_date=future_date,
    )

    service = AccountBalanceService()

    balance = service.get_account_balance(
        db=db,
        account_id=test_account.id,
        user_id=test_user.id,
    )

    assert balance == Decimal("10000.00")


def test_user_isolation(
    db,
    test_user,
    test_account,
    test_user_2,
    test_user_2_account,
    create_transfer,
):
    create_transfer(
        user_id=test_user_2.id,
        source_account_id=test_user_2_account.id,
        destination_account_id=test_account.id,
        amount="5000.00",
    )

    service = AccountBalanceService()

    balance = service.get_account_balance(
        db=db,
        account_id=test_account.id,
        user_id=test_user.id,
    )

    assert balance == Decimal("10000.00")


def test_total_balance_sums_all_user_accounts(
    db,
    test_user,
    test_account,
    test_account_2,
):
    service = AccountBalanceService()

    total_balance = service.get_total_balance(
        db=db,
        user_id=test_user.id,
    )

    assert total_balance == Decimal("15000.00")