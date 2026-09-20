from datetime import datetime, timezone
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.core.auth import get_current_user
from app.db.session import get_db
from app.main import app


@pytest.fixture
def client(db, test_user):
    def override_get_db():
        yield db

    def override_get_current_user():
        return test_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def transfer_payload(source_account_id, destination_account_id):
    return {
        "source_account_id": source_account_id,
        "destination_account_id": destination_account_id,
        "amount": "3000.00",
        "description": "Transfer to savings",
        "transfer_date": datetime.now(timezone.utc).isoformat(),
    }


def test_create_transfer_api_success(
    client,
    test_account,
    test_account_2,
):
    response = client.post(
        "/api/v1/transfers",
        json=transfer_payload(
            test_account.id,
            test_account_2.id,
        ),
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] is not None
    assert data["source_account_id"] == test_account.id
    assert data["destination_account_id"] == test_account_2.id
    assert Decimal(data["amount"]) == Decimal("3000.00")
    assert data["description"] == "Transfer to savings"


def test_create_transfer_api_rejects_same_account(
    client,
    test_account,
):
    response = client.post(
        "/api/v1/transfers",
        json=transfer_payload(
            test_account.id,
            test_account.id,
        ),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Source and destination accounts must be different."
    )


def test_create_transfer_api_rejects_negative_amount(
    client,
    test_account,
    test_account_2,
):
    payload = transfer_payload(
        test_account.id,
        test_account_2.id,
    )
    payload["amount"] = "-100.00"

    response = client.post(
        "/api/v1/transfers",
        json=payload,
    )

    assert response.status_code == 422


def test_create_transfer_api_rejects_invalid_source_account(
    client,
    test_account_2,
):
    response = client.post(
        "/api/v1/transfers",
        json=transfer_payload(
            999999,
            test_account_2.id,
        ),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Source account not found."


def test_create_transfer_api_rejects_invalid_destination_account(
    client,
    test_account,
):
    response = client.post(
        "/api/v1/transfers",
        json=transfer_payload(
            test_account.id,
            999999,
        ),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Destination account not found."


def test_get_transfer_api_success(
    client,
    test_account,
    test_account_2,
):
    create_response = client.post(
        "/api/v1/transfers",
        json=transfer_payload(
            test_account.id,
            test_account_2.id,
        ),
    )

    assert create_response.status_code == 201

    transfer_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/transfers/{transfer_id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == transfer_id
    assert data["source_account_id"] == test_account.id
    assert data["destination_account_id"] == test_account_2.id
    assert Decimal(data["amount"]) == Decimal("3000.00")


def test_get_transfers_api_returns_list(
    client,
    test_account,
    test_account_2,
):
    first_response = client.post(
        "/api/v1/transfers",
        json=transfer_payload(
            test_account.id,
            test_account_2.id,
        ),
    )

    second_payload = transfer_payload(
        test_account_2.id,
        test_account.id,
    )
    second_payload["amount"] = "500.00"

    second_response = client.post(
        "/api/v1/transfers",
        json=second_payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    response = client.get("/api/v1/transfers")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 2

    amounts = {Decimal(item["amount"]) for item in data}

    assert amounts == {
        Decimal("3000.00"),
        Decimal("500.00"),
    }


def test_get_nonexistent_transfer_api_returns_404(
    client,
):
    response = client.get(
        "/api/v1/transfers/999999",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Transfer not found."


def test_delete_transfer_api_success(
    client,
    test_account,
    test_account_2,
):
    create_response = client.post(
        "/api/v1/transfers",
        json=transfer_payload(
            test_account.id,
            test_account_2.id,
        ),
    )

    assert create_response.status_code == 201

    transfer_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/api/v1/transfers/{transfer_id}",
    )

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    get_response = client.get(
        f"/api/v1/transfers/{transfer_id}",
    )

    assert get_response.status_code == 404


def test_delete_nonexistent_transfer_api_returns_404(
    client,
):
    response = client.delete(
        "/api/v1/transfers/999999",
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Transfer not found."