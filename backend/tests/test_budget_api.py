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


def budget_payload(
    category_id: int,
    amount="10000.00",
    month=None,
    year=None,
):
    now = datetime.now(timezone.utc)

    return {
        "category_id": category_id,
        "amount": amount,
        "month": month if month is not None else now.month,
        "year": year if year is not None else now.year,
    }


def test_create_budget_success(
    db,
    test_user,
    expense_category,
):
    client = create_client(db, test_user)

    try:
        response = client.post(
            "/api/v1/budgets",
            json=budget_payload(
                expense_category.id,
            ),
        )

        assert response.status_code == 201

        body = response.json()

        assert body["id"] is not None
        assert body["category_id"] == expense_category.id
        assert body["amount"] == "10000.00"

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_create_budget_rejects_income_category(
    db,
    test_user,
    income_category,
):
    client = create_client(db, test_user)

    try:
        response = client.post(
            "/api/v1/budgets",
            json=budget_payload(
                income_category.id,
            ),
        )

        assert response.status_code == 400
        assert "expense categories" in response.json()["detail"]

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_create_budget_missing_category_returns_404(
    db,
    test_user,
):
    client = create_client(db, test_user)

    try:
        response = client.post(
            "/api/v1/budgets",
            json=budget_payload(
                999999,
            ),
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Category not found."

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_create_duplicate_budget_returns_409(
    db,
    test_user,
    expense_category,
):
    payload = budget_payload(
        expense_category.id,
    )

    client = create_client(db, test_user)

    try:
        first_response = client.post(
            "/api/v1/budgets",
            json=payload,
        )

        second_response = client.post(
            "/api/v1/budgets",
            json=payload,
        )

        assert first_response.status_code == 201
        assert second_response.status_code == 409
        assert second_response.json()["detail"] == (
            "Budget already exists."
        )

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_create_budget_rejects_invalid_month(
    db,
    test_user,
    expense_category,
):
    client = create_client(db, test_user)

    try:
        response = client.post(
            "/api/v1/budgets",
            json=budget_payload(
                expense_category.id,
                month=13,
            ),
        )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_create_budget_rejects_invalid_year(
    db,
    test_user,
    expense_category,
):
    client = create_client(db, test_user)

    try:
        response = client.post(
            "/api/v1/budgets",
            json=budget_payload(
                expense_category.id,
                year=1999,
            ),
        )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_get_budget_success(
    db,
    test_user,
    expense_category,
):
    client = create_client(db, test_user)

    try:
        created = client.post(
            "/api/v1/budgets",
            json=budget_payload(
                expense_category.id,
            ),
        )

        assert created.status_code == 201

        budget_id = created.json()["id"]

        response = client.get(
            f"/api/v1/budgets/{budget_id}",
        )

        assert response.status_code == 200
        assert response.json()["id"] == budget_id

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_get_missing_budget_returns_404(
    db,
    test_user,
):
    client = create_client(db, test_user)

    try:
        response = client.get(
            "/api/v1/budgets/999999",
        )

        assert response.status_code == 404

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_list_budgets_returns_current_users_budgets(
    db,
    test_user,
    expense_category,
):
    client = create_client(db, test_user)

    try:
        created = client.post(
            "/api/v1/budgets",
            json=budget_payload(
                expense_category.id,
            ),
        )

        assert created.status_code == 201

        response = client.get(
            "/api/v1/budgets",
        )

        assert response.status_code == 200

        body = response.json()

        assert len(body) == 1
        assert body[0]["id"] == created.json()["id"]

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_update_budget_success(
    db,
    test_user,
    expense_category,
):
    client = create_client(db, test_user)

    try:
        created = client.post(
            "/api/v1/budgets",
            json=budget_payload(
                expense_category.id,
                "10000.00",
            ),
        )

        assert created.status_code == 201

        budget_id = created.json()["id"]

        response = client.put(
            f"/api/v1/budgets/{budget_id}",
            json=budget_payload(
                expense_category.id,
                "15000.00",
            ),
        )

        assert response.status_code == 200
        assert response.json()["id"] == budget_id
        assert response.json()["amount"] == "15000.00"

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_update_missing_budget_returns_404(
    db,
    test_user,
    expense_category,
):
    client = create_client(db, test_user)

    try:
        response = client.put(
            "/api/v1/budgets/999999",
            json=budget_payload(
                expense_category.id,
            ),
        )

        assert response.status_code == 404

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_delete_budget_success(
    db,
    test_user,
    expense_category,
):
    client = create_client(db, test_user)

    try:
        created = client.post(
            "/api/v1/budgets",
            json=budget_payload(
                expense_category.id,
            ),
        )

        assert created.status_code == 201

        budget_id = created.json()["id"]

        response = client.delete(
            f"/api/v1/budgets/{budget_id}",
        )

        assert response.status_code == 204
        assert response.content == b""

        get_response = client.get(
            f"/api/v1/budgets/{budget_id}",
        )

        assert get_response.status_code == 404

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_delete_missing_budget_returns_404(
    db,
    test_user,
):
    client = create_client(db, test_user)

    try:
        response = client.delete(
            "/api/v1/budgets/999999",
        )

        assert response.status_code == 404

    finally:
        app.dependency_overrides.clear()
        client.close()