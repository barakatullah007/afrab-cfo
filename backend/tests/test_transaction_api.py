from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.core.auth import get_current_user
from app.db.session import get_db
from app.main import app


def create_client(db, user):
    def override_get_db():
        yield db

    def override_get_current_user():
        return user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    return TestClient(app)


def transaction_payload(
    account_id: int,
    category_id: int,
    amount: str = "250.00",
):
    return {
        "account_id": account_id,
        "category_id": category_id,
        "description": "Lunch",
        "merchant": "Test Merchant",
        "amount": amount,
        "notes": "Test transaction",
        "transaction_date": datetime.now(timezone.utc).isoformat(),
    }


def test_create_transaction_success(
    db,
    test_user,
    test_account,
    expense_category,
):
    client = create_client(db, test_user)

    try:
        response = client.post(
            "/api/v1/transactions",
            json=transaction_payload(
                test_account.id,
                expense_category.id,
            ),
        )

        assert response.status_code == 201

        body = response.json()

        assert body["id"] is not None
        assert body["account_id"] == test_account.id
        assert body["category_id"] == expense_category.id
        assert body["amount"] == "250.00"
        assert body["description"] == "Lunch"

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_create_transaction_invalid_account_returns_404(
    db,
    test_user,
    expense_category,
):
    client = create_client(db, test_user)

    try:
        response = client.post(
            "/api/v1/transactions",
            json=transaction_payload(
                999999,
                expense_category.id,
            ),
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Account not found."

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_create_transaction_invalid_category_returns_404(
    db,
    test_user,
    test_account,
):
    client = create_client(db, test_user)

    try:
        response = client.post(
            "/api/v1/transactions",
            json=transaction_payload(
                test_account.id,
                999999,
            ),
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Category not found."

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_create_transaction_negative_amount_returns_422(
    db,
    test_user,
    test_account,
    expense_category,
):
    client = create_client(db, test_user)

    try:
        response = client.post(
            "/api/v1/transactions",
            json=transaction_payload(
                test_account.id,
                expense_category.id,
                "-100.00",
            ),
        )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_create_transaction_zero_amount_returns_422(
    db,
    test_user,
    test_account,
    expense_category,
):
    client = create_client(db, test_user)

    try:
        response = client.post(
            "/api/v1/transactions",
            json=transaction_payload(
                test_account.id,
                expense_category.id,
                "0.00",
            ),
        )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_get_transaction_success(
    db,
    test_user,
    test_account,
    expense_category,
):
    client = create_client(db, test_user)

    try:
        created = client.post(
            "/api/v1/transactions",
            json=transaction_payload(
                test_account.id,
                expense_category.id,
            ),
        )

        assert created.status_code == 201

        transaction_id = created.json()["id"]

        response = client.get(
            f"/api/v1/transactions/{transaction_id}",
        )

        assert response.status_code == 200
        assert response.json()["id"] == transaction_id

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_get_missing_transaction_returns_404(
    db,
    test_user,
):
    client = create_client(db, test_user)

    try:
        response = client.get(
            "/api/v1/transactions/999999",
        )

        assert response.status_code == 404

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_get_other_users_transaction_returns_404(
    db,
    test_user,
    test_user_2,
    test_account,
    expense_category,
):
    client = create_client(db, test_user)

    try:
        created = client.post(
            "/api/v1/transactions",
            json=transaction_payload(
                test_account.id,
                expense_category.id,
            ),
        )

        transaction_id = created.json()["id"]

    finally:
        app.dependency_overrides.clear()
        client.close()

    other_client = create_client(db, test_user_2)

    try:
        response = other_client.get(
            f"/api/v1/transactions/{transaction_id}",
        )

        assert response.status_code == 404

    finally:
        app.dependency_overrides.clear()
        other_client.close()


def test_list_transactions_returns_current_users_transactions(
    db,
    test_user,
    test_account,
    expense_category,
):
    client = create_client(db, test_user)

    try:
        first = client.post(
            "/api/v1/transactions",
            json=transaction_payload(
                test_account.id,
                expense_category.id,
                "100.00",
            ),
        )

        second = client.post(
            "/api/v1/transactions",
            json=transaction_payload(
                test_account.id,
                expense_category.id,
                "200.00",
            ),
        )

        assert first.status_code == 201
        assert second.status_code == 201

        response = client.get("/api/v1/transactions")

        assert response.status_code == 200

        body = response.json()

        assert len(body) == 2

        amounts = {item["amount"] for item in body}

        assert amounts == {"100.00", "200.00"}

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_update_transaction_success(
    db,
    test_user,
    test_account,
    test_account_2,
    expense_category,
):
    client = create_client(db, test_user)

    try:
        created = client.post(
            "/api/v1/transactions",
            json=transaction_payload(
                test_account.id,
                expense_category.id,
            ),
        )

        assert created.status_code == 201

        transaction_id = created.json()["id"]

        response = client.put(
            f"/api/v1/transactions/{transaction_id}",
            json=transaction_payload(
                test_account_2.id,
                expense_category.id,
                "600.00",
            ),
        )

        assert response.status_code == 200

        body = response.json()

        assert body["id"] == transaction_id
        assert body["account_id"] == test_account_2.id
        assert body["amount"] == "600.00"

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_update_missing_transaction_returns_404(
    db,
    test_user,
    test_account,
    expense_category,
):
    client = create_client(db, test_user)

    try:
        response = client.put(
            "/api/v1/transactions/999999",
            json=transaction_payload(
                test_account.id,
                expense_category.id,
            ),
        )

        assert response.status_code == 404

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_delete_transaction_success(
    db,
    test_user,
    test_account,
    expense_category,
):
    client = create_client(db, test_user)

    try:
        created = client.post(
            "/api/v1/transactions",
            json=transaction_payload(
                test_account.id,
                expense_category.id,
            ),
        )

        assert created.status_code == 201

        transaction_id = created.json()["id"]

        delete_response = client.delete(
            f"/api/v1/transactions/{transaction_id}",
        )

        assert delete_response.status_code == 204
        assert delete_response.content == b""

        get_response = client.get(
            f"/api/v1/transactions/{transaction_id}",
        )

        assert get_response.status_code == 404

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_delete_missing_transaction_returns_404(
    db,
    test_user,
):
    client = create_client(db, test_user)

    try:
        response = client.delete(
            "/api/v1/transactions/999999",
        )

        assert response.status_code == 404

    finally:
        app.dependency_overrides.clear()
        client.close()