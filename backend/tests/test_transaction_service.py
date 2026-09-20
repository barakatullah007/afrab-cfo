from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.schemas.transaction import TransactionCreate, TransactionUpdate
from app.services.transaction_service import TransactionService


def transaction_data(
    account_id: int,
    category_id: int,
    amount: str = "250.00",
):
    return TransactionCreate(
        account_id=account_id,
        category_id=category_id,
        description="Lunch",
        merchant="Test Merchant",
        amount=Decimal(amount),
        notes="Test transaction",
        transaction_date=datetime.now(timezone.utc),
    )


def test_create_transaction_success(
    db,
    test_user,
    test_account,
    expense_category,
):
    service = TransactionService()

    transaction = service.create_transaction(
        db=db,
        current_user=test_user,
        transaction_data=transaction_data(
            test_account.id,
            expense_category.id,
        ),
    )

    assert transaction.id is not None
    assert transaction.user_id == test_user.id
    assert transaction.account_id == test_account.id
    assert transaction.category_id == expense_category.id
    assert transaction.amount == Decimal("250.00")
    assert transaction.description == "Lunch"


def test_create_transaction_rejects_other_users_account(
    db,
    test_user,
    test_user_2_account,
    expense_category,
):
    service = TransactionService()

    with pytest.raises(ValueError, match="Account not found."):
        service.create_transaction(
            db=db,
            current_user=test_user,
            transaction_data=transaction_data(
                test_user_2_account.id,
                expense_category.id,
            ),
        )


def test_create_transaction_rejects_other_users_category(
    db,
    test_user,
    test_account,
    test_user_2,
):
    from app.enums.category import CategoryType
    from app.models.category import Category

    other_category = Category(
        user_id=test_user_2.id,
        name="Other Expense",
        type=CategoryType.EXPENSE,
        icon="expense",
        color="#000000",
        is_default=False,
    )

    db.add(other_category)
    db.commit()
    db.refresh(other_category)

    service = TransactionService()

    with pytest.raises(ValueError, match="Category not found."):
        service.create_transaction(
            db=db,
            current_user=test_user,
            transaction_data=transaction_data(
                test_account.id,
                other_category.id,
            ),
        )


def test_get_transaction_success(
    db,
    test_user,
    test_account,
    expense_category,
):
    service = TransactionService()

    created = service.create_transaction(
        db=db,
        current_user=test_user,
        transaction_data=transaction_data(
            test_account.id,
            expense_category.id,
        ),
    )

    result = service.get_transaction(
        db=db,
        transaction_id=created.id,
        current_user=test_user,
    )

    assert result is not None
    assert result.id == created.id
    assert result.user_id == test_user.id


def test_get_transaction_returns_none_for_other_user(
    db,
    test_user,
    test_user_2,
    test_account,
    expense_category,
):
    service = TransactionService()

    transaction = service.create_transaction(
        db=db,
        current_user=test_user,
        transaction_data=transaction_data(
            test_account.id,
            expense_category.id,
        ),
    )

    result = service.get_transaction(
        db=db,
        transaction_id=transaction.id,
        current_user=test_user_2,
    )

    assert result is None


def test_get_transactions_is_user_scoped(
    db,
    test_user,
    test_user_2,
    test_account,
    test_user_2_account,
    expense_category,
):
    from app.enums.category import CategoryType
    from app.models.category import Category

    other_category = Category(
        user_id=test_user_2.id,
        name="Other Expense",
        type=CategoryType.EXPENSE,
        icon="expense",
        color="#000000",
        is_default=False,
    )

    db.add(other_category)
    db.commit()
    db.refresh(other_category)

    service = TransactionService()

    first = service.create_transaction(
        db=db,
        current_user=test_user,
        transaction_data=transaction_data(
            test_account.id,
            expense_category.id,
            "250.00",
        ),
    )

    service.create_transaction(
        db=db,
        current_user=test_user_2,
        transaction_data=transaction_data(
            test_user_2_account.id,
            other_category.id,
            "900.00",
        ),
    )

    transactions = service.get_transactions(
        db=db,
        current_user=test_user,
    )

    assert len(transactions) == 1
    assert transactions[0].id == first.id
    assert transactions[0].user_id == test_user.id


def test_update_transaction_success(
    db,
    test_user,
    test_account,
    test_account_2,
    expense_category,
):
    service = TransactionService()

    transaction = service.create_transaction(
        db=db,
        current_user=test_user,
        transaction_data=transaction_data(
            test_account.id,
            expense_category.id,
            "250.00",
        ),
    )

    updated = service.update_transaction(
        db=db,
        transaction_id=transaction.id,
        current_user=test_user,
        transaction_data=TransactionUpdate(
            account_id=test_account_2.id,
            category_id=expense_category.id,
            description="Updated transaction",
            merchant="Updated Merchant",
            amount=Decimal("600.00"),
            notes="Updated",
            transaction_date=datetime.now(timezone.utc),
        ),
    )

    assert updated is not None
    assert updated.id == transaction.id
    assert updated.account_id == test_account_2.id
    assert updated.amount == Decimal("600.00")
    assert updated.description == "Updated transaction"
    assert updated.merchant == "Updated Merchant"


def test_update_transaction_rejects_other_users_account(
    db,
    test_user,
    test_user_2_account,
    test_account,
    expense_category,
):
    service = TransactionService()

    transaction = service.create_transaction(
        db=db,
        current_user=test_user,
        transaction_data=transaction_data(
            test_account.id,
            expense_category.id,
        ),
    )

    with pytest.raises(ValueError, match="Account not found."):
        service.update_transaction(
            db=db,
            transaction_id=transaction.id,
            current_user=test_user,
            transaction_data=TransactionUpdate(
                account_id=test_user_2_account.id,
                category_id=expense_category.id,
                description="Invalid update",
                merchant="Test",
                amount=Decimal("100.00"),
                notes=None,
                transaction_date=datetime.now(timezone.utc),
            ),
        )


def test_update_transaction_returns_none_for_missing_transaction(
    db,
    test_user,
    test_account,
    expense_category,
):
    service = TransactionService()

    result = service.update_transaction(
        db=db,
        transaction_id=999999,
        current_user=test_user,
        transaction_data=TransactionUpdate(
            account_id=test_account.id,
            category_id=expense_category.id,
            description="Missing",
            merchant="Test",
            amount=Decimal("100.00"),
            notes=None,
            transaction_date=datetime.now(timezone.utc),
        ),
    )

    assert result is None


def test_delete_transaction_success(
    db,
    test_user,
    test_account,
    expense_category,
):
    service = TransactionService()

    transaction = service.create_transaction(
        db=db,
        current_user=test_user,
        transaction_data=transaction_data(
            test_account.id,
            expense_category.id,
        ),
    )

    deleted = service.delete_transaction(
        db=db,
        transaction_id=transaction.id,
        current_user=test_user,
    )

    assert deleted is not None
    assert deleted.id == transaction.id

    result = service.get_transaction(
        db=db,
        transaction_id=transaction.id,
        current_user=test_user,
    )

    assert result is None


def test_delete_transaction_cannot_delete_other_users_transaction(
    db,
    test_user,
    test_user_2,
    test_account,
    expense_category,
):
    service = TransactionService()

    transaction = service.create_transaction(
        db=db,
        current_user=test_user,
        transaction_data=transaction_data(
            test_account.id,
            expense_category.id,
        ),
    )

    result = service.delete_transaction(
        db=db,
        transaction_id=transaction.id,
        current_user=test_user_2,
    )

    assert result is None

    still_exists = service.get_transaction(
        db=db,
        transaction_id=transaction.id,
        current_user=test_user,
    )

    assert still_exists is not None
    