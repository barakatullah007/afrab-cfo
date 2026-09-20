from datetime import datetime, timezone
from decimal import Decimal

import pytest
from fastapi import HTTPException

from app.schemas.transfer import TransferCreate
from app.services.transfer_service import TransferService
from app.models.account import Account
from app.enums.account import AccountType


@pytest.fixture
def transfer_service():
    return TransferService()


def test_create_transfer_success(
    db,
    test_user,
    test_account,
    test_account_2,
    transfer_service,
):
    data = TransferCreate(
        source_account_id=test_account.id,
        destination_account_id=test_account_2.id,
        amount=Decimal("3000.00"),
        description="Transfer to savings",
        transfer_date=datetime.now(timezone.utc),
    )

    transfer = transfer_service.create_transfer(
        db=db,
        current_user=test_user,
        data=data,
    )

    assert transfer.id is not None
    assert transfer.user_id == test_user.id
    assert transfer.source_account_id == test_account.id
    assert transfer.destination_account_id == test_account_2.id
    assert transfer.amount == Decimal("3000.00")
    assert transfer.description == "Transfer to savings"


def test_create_transfer_rejects_same_account(
    db,
    test_user,
    test_account,
    transfer_service,
):
    data = TransferCreate(
        source_account_id=test_account.id,
        destination_account_id=test_account.id,
        amount=Decimal("1000.00"),
        description="Invalid transfer",
        transfer_date=datetime.now(timezone.utc),
    )

    with pytest.raises(HTTPException) as exc_info:
        transfer_service.create_transfer(
            db=db,
            current_user=test_user,
            data=data,
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == (
        "Source and destination accounts must be different."
    )


def test_create_transfer_rejects_source_account_owned_by_another_user(
    db,
    test_user,
    test_account_2,
    test_user_2_account,
    transfer_service,
):
    data = TransferCreate(
        source_account_id=test_user_2_account.id,
        destination_account_id=test_account_2.id,
        amount=Decimal("1000.00"),
        description="Invalid ownership",
        transfer_date=datetime.now(timezone.utc),
    )

    with pytest.raises(HTTPException) as exc_info:
        transfer_service.create_transfer(
            db=db,
            current_user=test_user,
            data=data,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Source account not found."


def test_create_transfer_rejects_destination_account_owned_by_another_user(
    db,
    test_user,
    test_account,
    test_user_2_account,
    transfer_service,
):
    data = TransferCreate(
        source_account_id=test_account.id,
        destination_account_id=test_user_2_account.id,
        amount=Decimal("1000.00"),
        description="Invalid ownership",
        transfer_date=datetime.now(timezone.utc),
    )

    with pytest.raises(HTTPException) as exc_info:
        transfer_service.create_transfer(
            db=db,
            current_user=test_user,
            data=data,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Destination account not found."


def test_create_transfer_rejects_different_currencies(
    db,
    test_user,
    test_account,
    transfer_service,
):
    usd_account = Account(
        user_id=test_user.id,
        name="USD Account",
        type=AccountType.BANK,
        opening_balance=Decimal("1000.00"),
        currency="USD",
        icon="bank",
        color="#000000",
        is_default=False,
    )

    db.add(usd_account)
    db.commit()
    db.refresh(usd_account)

    data = TransferCreate(
        source_account_id=test_account.id,
        destination_account_id=usd_account.id,
        amount=Decimal("1000.00"),
        description="Currency mismatch",
        transfer_date=datetime.now(timezone.utc),
    )

    with pytest.raises(HTTPException) as exc_info:
        transfer_service.create_transfer(
            db=db,
            current_user=test_user,
            data=data,
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == (
        "Transfers between different currencies are not supported yet."
    )


def test_get_transfer_success(
    db,
    test_user,
    test_account,
    test_account_2,
    create_transfer,
    transfer_service,
):
    transfer = create_transfer(
        user_id=test_user.id,
        source_account_id=test_account.id,
        destination_account_id=test_account_2.id,
        amount="2500.00",
        description="Test transfer",
    )

    result = transfer_service.get_transfer(
        db=db,
        transfer_id=transfer.id,
        current_user=test_user,
    )

    assert result.id == transfer.id
    assert result.user_id == test_user.id
    assert result.amount == Decimal("2500.00")


def test_get_transfer_rejects_another_users_transfer(
    db,
    test_user,
    test_user_2,
    test_account,
    test_account_2,
    test_user_2_account,
    create_transfer,
    transfer_service,
):
    transfer = create_transfer(
        user_id=test_user.id,
        source_account_id=test_account.id,
        destination_account_id=test_account_2.id,
        amount="2500.00",
    )

    with pytest.raises(HTTPException) as exc_info:
        transfer_service.get_transfer(
            db=db,
            transfer_id=transfer.id,
            current_user=test_user_2,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Transfer not found."


def test_get_transfers_returns_only_current_users_transfers(
    db,
    test_user,
    test_user_2,
    test_account,
    test_account_2,
    test_user_2_account,
    create_transfer,
    transfer_service,
):
    transfer_1 = create_transfer(
        user_id=test_user.id,
        source_account_id=test_account.id,
        destination_account_id=test_account_2.id,
        amount="1000.00",
        description="User 1 transfer",
    )

    transfer_2 = create_transfer(
        user_id=test_user.id,
        source_account_id=test_account_2.id,
        destination_account_id=test_account.id,
        amount="500.00",
        description="User 1 transfer 2",
    )

    other_user_transfer = create_transfer(
        user_id=test_user_2.id,
        source_account_id=test_user_2_account.id,
        destination_account_id=test_user_2_account.id,
        amount="2000.00",
        description="Other user transfer",
    )

    transfers = transfer_service.get_transfers(
        db=db,
        current_user=test_user,
    )

    transfer_ids = {transfer.id for transfer in transfers}

    assert transfer_ids == {transfer_1.id, transfer_2.id}
    assert other_user_transfer.id not in transfer_ids

def test_delete_transfer_success(
    db,
    test_user,
    test_account,
    test_account_2,
    create_transfer,
    transfer_service,
):
    transfer = create_transfer(
        user_id=test_user.id,
        source_account_id=test_account.id,
        destination_account_id=test_account_2.id,
        amount="1500.00",
    )

    transfer_service.delete_transfer(
        db=db,
        transfer_id=transfer.id,
        current_user=test_user,
    )

    with pytest.raises(HTTPException) as exc_info:
        transfer_service.get_transfer(
            db=db,
            transfer_id=transfer.id,
            current_user=test_user,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Transfer not found."

def test_delete_transfer_rejects_nonexistent_transfer(
    db,
    test_user,
    transfer_service,
):
    with pytest.raises(HTTPException) as exc_info:
        transfer_service.delete_transfer(
            db=db,
            transfer_id=999999,
            current_user=test_user,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Transfer not found."