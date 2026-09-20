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


def recurring_payload(
    account_id: int,
    category_id: int,
    transaction_type="expense",
    frequency="monthly",
    title="Monthly Rent",
    amount="11000.00",
):
    return {
        "account_id": account_id,
        "category_id": category_id,
        "title": title,
        "description": "Monthly recurring transaction",
        "amount": amount,
        "transaction_type": transaction_type,
        "frequency": frequency,
        "start_date": "2026-09-01T00:00:00Z",
        "end_date": "2027-09-01T00:00:00Z",
        "next_run_date": "2026-10-01T00:00:00Z",
    }


def test_create_recurring_transaction_success(
    db,
    test_user,
    test_account,
    expense_category,
):
    client = create_client(db, test_user)

    try:
        response = client.post(
            "/api/v1/recurring-transactions",
            json=recurring_payload(
                test_account.id,
                expense_category.id,
            ),
        )

        assert response.status_code == 201

        body = response.json()

        assert body["id"] is not None
        assert body["account_id"] == test_account.id
        assert body["category_id"] == expense_category.id
        assert body["title"] == "Monthly Rent"
        assert body["amount"] == "11000.00"
        assert body["transaction_type"] == "expense"
        assert body["frequency"] == "monthly"
        assert body["is_active"] is True

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_create_recurring_transaction_rejects_invalid_account(
    db,
    test_user,
    expense_category,
):
    client = create_client(db, test_user)

    try:
        response = client.post(
            "/api/v1/recurring-transactions",
            json=recurring_payload(
                999999,
                expense_category.id,
            ),
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Account not found."

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_create_recurring_transaction_rejects_invalid_category(
    db,
    test_user,
    test_account,
):
    client = create_client(db, test_user)

    try:
        response = client.post(
            "/api/v1/recurring-transactions",
            json=recurring_payload(
                test_account.id,
                999999,
            ),
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Category not found."

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_create_recurring_transaction_rejects_negative_amount(
    db,
    test_user,
    test_account,
    expense_category,
):
    client = create_client(db, test_user)

    try:
        response = client.post(
            "/api/v1/recurring-transactions",
            json=recurring_payload(
                test_account.id,
                expense_category.id,
                amount="-100.00",
            ),
        )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_create_recurring_transaction_rejects_invalid_frequency(
    db,
    test_user,
    test_account,
    expense_category,
):
    client = create_client(db, test_user)

    try:
        response = client.post(
            "/api/v1/recurring-transactions",
            json=recurring_payload(
                test_account.id,
                expense_category.id,
                frequency="invalid",
            ),
        )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_create_recurring_transaction_rejects_end_date_before_start_date(
    db,
    test_user,
    test_account,
    expense_category,
):
    payload = recurring_payload(
        test_account.id,
        expense_category.id,
    )

    payload["start_date"] = "2026-10-01T00:00:00Z"
    payload["end_date"] = "2026-09-01T00:00:00Z"

    client = create_client(db, test_user)

    try:
        response = client.post(
            "/api/v1/recurring-transactions",
            json=payload,
        )

        assert response.status_code == 422
        assert "End date cannot be before start date." in str(
            response.json()
        )

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_get_recurring_transactions(
    db,
    test_user,
    test_account,
    expense_category,
):
    client = create_client(db, test_user)

    try:
        first = client.post(
            "/api/v1/recurring-transactions",
            json=recurring_payload(
                test_account.id,
                expense_category.id,
                title="Rent",
            ),
        )

        second = client.post(
            "/api/v1/recurring-transactions",
            json=recurring_payload(
                test_account.id,
                expense_category.id,
                title="Internet",
                amount="1000.00",
            ),
        )

        assert first.status_code == 201
        assert second.status_code == 201

        response = client.get(
            "/api/v1/recurring-transactions",
        )

        assert response.status_code == 200

        body = response.json()

        assert len(body) == 2
        assert {item["title"] for item in body} == {
            "Rent",
            "Internet",
        }

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_get_recurring_transaction_success(
    db,
    test_user,
    test_account,
    expense_category,
):
    client = create_client(db, test_user)

    try:
        created = client.post(
            "/api/v1/recurring-transactions",
            json=recurring_payload(
                test_account.id,
                expense_category.id,
            ),
        )

        assert created.status_code == 201

        recurring_id = created.json()["id"]

        response = client.get(
            f"/api/v1/recurring-transactions/{recurring_id}",
        )

        assert response.status_code == 200
        assert response.json()["id"] == recurring_id

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_get_missing_recurring_transaction_returns_404(
    db,
    test_user,
):
    client = create_client(db, test_user)

    try:
        response = client.get(
            "/api/v1/recurring-transactions/999999",
        )

        assert response.status_code == 404
        assert response.json()["detail"] == (
            "Recurring transaction not found"
        )

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_update_recurring_transaction_success(
    db,
    test_user,
    test_account,
    expense_category,
):
    client = create_client(db, test_user)

    try:
        created = client.post(
            "/api/v1/recurring-transactions",
            json=recurring_payload(
                test_account.id,
                expense_category.id,
            ),
        )

        assert created.status_code == 201

        recurring_id = created.json()["id"]

        payload = recurring_payload(
            test_account.id,
            expense_category.id,
            title="Updated Rent",
            amount="12000.00",
        )

        payload["is_active"] = True

        response = client.put(
            f"/api/v1/recurring-transactions/{recurring_id}",
            json=payload,
        )

        assert response.status_code == 200

        body = response.json()

        assert body["id"] == recurring_id
        assert body["title"] == "Updated Rent"
        assert body["amount"] == "12000.00"

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_update_missing_recurring_transaction_returns_404(
    db,
    test_user,
    test_account,
    expense_category,
):
    client = create_client(db, test_user)

    try:
        response = client.put(
            "/api/v1/recurring-transactions/999999",
            json=recurring_payload(
                test_account.id,
                expense_category.id,
            ),
        )

        assert response.status_code == 404

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_delete_recurring_transaction_success(
    db,
    test_user,
    test_account,
    expense_category,
):
    client = create_client(db, test_user)

    try:
        created = client.post(
            "/api/v1/recurring-transactions",
            json=recurring_payload(
                test_account.id,
                expense_category.id,
            ),
        )

        assert created.status_code == 201

        recurring_id = created.json()["id"]

        response = client.delete(
            f"/api/v1/recurring-transactions/{recurring_id}",
        )

        assert response.status_code == 204
        assert response.content == b""

        get_response = client.get(
            f"/api/v1/recurring-transactions/{recurring_id}",
        )

        assert get_response.status_code == 404

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_activate_and_deactivate_recurring_transaction(
    db,
    test_user,
    test_account,
    expense_category,
):
    client = create_client(db, test_user)

    try:
        created = client.post(
            "/api/v1/recurring-transactions",
            json=recurring_payload(
                test_account.id,
                expense_category.id,
            ),
        )

        assert created.status_code == 201

        recurring_id = created.json()["id"]

        deactivate = client.patch(
            f"/api/v1/recurring-transactions/{recurring_id}/deactivate",
        )

        assert deactivate.status_code == 200
        assert deactivate.json()["is_active"] is False

        activate = client.patch(
            f"/api/v1/recurring-transactions/{recurring_id}/activate",
        )

        assert activate.status_code == 200
        assert activate.json()["is_active"] is True

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_deactivate_missing_recurring_transaction_returns_404(
    db,
    test_user,
):
    client = create_client(db, test_user)

    try:
        response = client.patch(
            "/api/v1/recurring-transactions/999999/deactivate",
        )

        assert response.status_code == 404
        assert response.json()["detail"] == (
            "Recurring transaction not found"
        )

    finally:
        app.dependency_overrides.clear()
        client.close()