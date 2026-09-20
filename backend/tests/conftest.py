from datetime import datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

import app.models

from app.core.config import settings
from app.db.base import Base
from app.models.account import Account
from app.models.category import Category
from app.models.transfer import Transfer
from app.models.transaction import Transaction
from app.models.user import User
from app.enums.account import AccountType
from app.enums.category import CategoryType


# Use the application's PostgreSQL connection settings,
# but point the tests to the dedicated test database.
test_database_url = make_url(settings.database_url).set(
    database="afrab_cfo_test"
)

engine = create_engine(
    test_database_url,
    echo=False,
)


@pytest.fixture
def db():
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    Base.metadata.drop_all(engine)


@pytest.fixture
def test_user(db):
    user = User(
        name="Test User",
        email="test@example.com",
        password_hash="test-password-hash",
        auth_provider="local",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@pytest.fixture
def test_user_2(db):
    user = User(
        name="Second Test User",
        email="second@example.com",
        password_hash="test-password-hash",
        auth_provider="local",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@pytest.fixture
def test_account(db, test_user):
    account = Account(
        user_id=test_user.id,
        name="Test Bank",
        type=AccountType.BANK,
        opening_balance=Decimal("10000.00"),
        currency="INR",
        icon="bank",
        color="#000000",
        is_default=False,
    )

    db.add(account)
    db.commit()
    db.refresh(account)

    return account


@pytest.fixture
def test_account_2(db, test_user):
    account = Account(
        user_id=test_user.id,
        name="Test Savings",
        type=AccountType.SAVINGS,
        opening_balance=Decimal("5000.00"),
        currency="INR",
        icon="savings",
        color="#000000",
        is_default=False,
    )

    db.add(account)
    db.commit()
    db.refresh(account)

    return account


@pytest.fixture
def test_user_2_account(db, test_user_2):
    account = Account(
        user_id=test_user_2.id,
        name="Other User Account",
        type=AccountType.BANK,
        opening_balance=Decimal("20000.00"),
        currency="INR",
        icon="bank",
        color="#000000",
        is_default=False,
    )

    db.add(account)
    db.commit()
    db.refresh(account)

    return account


@pytest.fixture
def income_category(db, test_user):
    category = Category(
        user_id=test_user.id,
        name="Salary",
        type=CategoryType.INCOME,
        icon="salary",
        color="#000000",
        is_default=False,
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


@pytest.fixture
def expense_category(db, test_user):
    category = Category(
        user_id=test_user.id,
        name="Food",
        type=CategoryType.EXPENSE,
        icon="food",
        color="#000000",
        is_default=False,
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


@pytest.fixture
def create_transaction(db):
    def _create_transaction(
        *,
        user_id,
        account_id,
        category_id,
        amount,
        transaction_date=None,
        description="Test transaction",
    ):
        transaction = Transaction(
            user_id=user_id,
            account_id=account_id,
            category_id=category_id,
            description=description,
            merchant=None,
            amount=Decimal(str(amount)),
            notes=None,
            transaction_date=transaction_date or datetime.now(timezone.utc),
        )

        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        return transaction

    return _create_transaction


@pytest.fixture
def create_transfer(db):
    def _create_transfer(
        *,
        user_id,
        source_account_id,
        destination_account_id,
        amount,
        transfer_date=None,
        description="Test transfer",
    ):
        transfer = Transfer(
            user_id=user_id,
            source_account_id=source_account_id,
            destination_account_id=destination_account_id,
            amount=Decimal(str(amount)),
            description=description,
            transfer_date=transfer_date or datetime.now(timezone.utc),
        )

        db.add(transfer)
        db.commit()
        db.refresh(transfer)

        return transfer

    return _create_transfer