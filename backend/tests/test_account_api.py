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


def account_payload(
    name="Savings Account",
    account_type="savings",
    opening_balance="5000.00",
    currency="INR",
    icon="savings",
    color="#22c55e",
):
    return {
        "name": name,
        "type": account_type,
        "opening_balance": opening_balance,
        "currency": currency,
        "icon": icon,
        "color": color,
    }


def test_create_account_success(db, test_user):
    client = create_client(db, test_user)

    try:
        response = client.post(
            "/api/v1/accounts",
            json=account_payload(),
        )

        assert response.status_code == 201

        body = response.json()

        assert body["name"] == "Savings Account"
        assert body["type"] == "savings"
        assert body["opening_balance"] == "5000.00"
        assert body["currency"] == "INR"
        assert body["icon"] == "savings"
        assert body["color"] == "#22c55e"
        assert body["is_default"] is False
        assert body["id"] is not None
        assert body["created_at"] is not None

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_create_duplicate_account_returns_409(
    db,
    test_user,
    test_account,
):
    client = create_client(db, test_user)

    try:
        response = client.post(
            "/api/v1/accounts",
            json=account_payload(
                name=test_account.name,
            ),
        )

        assert response.status_code == 409
        assert response.json()["detail"] == "Account already exists."

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_create_account_with_negative_opening_balance_returns_422(
    db,
    test_user,
):
    client = create_client(db, test_user)

    try:
        response = client.post(
            "/api/v1/accounts",
            json=account_payload(
                opening_balance="-100.00",
            ),
        )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_create_account_missing_required_field_returns_422(
    db,
    test_user,
):
    client = create_client(db, test_user)

    try:
        payload = account_payload()
        del payload["name"]

        response = client.post(
            "/api/v1/accounts",
            json=payload,
        )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_get_accounts_returns_current_users_accounts_only(
    db,
    test_user,
    test_account,
    test_user_2_account,
):
    client = create_client(db, test_user)

    try:
        response = client.get("/api/v1/accounts")

        assert response.status_code == 200

        body = response.json()

        assert len(body) == 1
        assert body[0]["id"] == test_account.id
        assert body[0]["name"] == test_account.name

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_get_accounts_returns_empty_list_when_user_has_no_accounts(
    db,
    test_user,
):
    client = create_client(db, test_user)

    try:
        response = client.get("/api/v1/accounts")

        assert response.status_code == 200
        assert response.json() == []

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_update_account_success(
    db,
    test_user,
    test_account,
):
    client = create_client(db, test_user)

    try:
        response = client.put(
            f"/api/v1/accounts/{test_account.id}",
            json=account_payload(
                name="Updated Bank",
                account_type="bank",
                opening_balance="15000.00",
                currency="INR",
                icon="bank",
                color="#2563eb",
            ),
        )

        assert response.status_code == 200

        body = response.json()

        assert body["id"] == test_account.id
        assert body["name"] == "Updated Bank"

        # The current AccountService implementation updates
        # name, icon and color only.
        assert body["icon"] == "bank"
        assert body["color"] == "#2563eb"

        assert body["type"] == "bank"
        assert body["opening_balance"] == "10000.00"
        assert body["currency"] == "INR"

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_update_missing_account_returns_404(
    db,
    test_user,
):
    client = create_client(db, test_user)

    try:
        response = client.put(
            "/api/v1/accounts/999999",
            json=account_payload(
                name="Missing Account",
            ),
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Account not found"

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_update_other_users_account_returns_404(
    db,
    test_user,
    test_user_2_account,
):
    client = create_client(db, test_user)

    try:
        response = client.put(
            f"/api/v1/accounts/{test_user_2_account.id}",
            json=account_payload(
                name="Attempted Update",
            ),
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Account not found"

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_delete_account_success(
    db,
    test_user,
    test_account,
):
    client = create_client(db, test_user)

    try:
        response = client.delete(
            f"/api/v1/accounts/{test_account.id}",
        )

        assert response.status_code == 204
        assert response.content == b""

        get_response = client.get("/api/v1/accounts")

        assert get_response.status_code == 200
        assert get_response.json() == []

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_delete_missing_account_returns_404(
    db,
    test_user,
):
    client = create_client(db, test_user)

    try:
        response = client.delete(
            "/api/v1/accounts/999999",
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Account not found"

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_delete_other_users_account_returns_404(
    db,
    test_user,
    test_user_2_account,
):
    client = create_client(db, test_user)

    try:
        response = client.delete(
            f"/api/v1/accounts/{test_user_2_account.id}",
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Account not found"

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_delete_default_account_returns_400(
    db,
    test_user,
    test_account,
):
    test_account.is_default = True
    db.commit()
    db.refresh(test_account)

    client = create_client(db, test_user)

    try:
        response = client.delete(
            f"/api/v1/accounts/{test_account.id}",
        )

        assert response.status_code == 400
        assert response.json()["detail"] == (
            "Default accounts cannot be deleted."
        )

    finally:
        app.dependency_overrides.clear()
        client.close()