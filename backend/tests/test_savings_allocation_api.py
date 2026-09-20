from datetime import datetime, timezone
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.core.auth import get_current_user
from app.db.session import get_db
from app.main import app
from app.enums.category import CategoryType
from app.models.category import Category


TEST_MONTH = 9
TEST_YEAR = 2026


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


@pytest.fixture
def seeded_monthly_savings(
    test_user,
    test_account,
    income_category,
    expense_category,
    create_transaction,
):
    transaction_date = datetime(
        TEST_YEAR,
        TEST_MONTH,
        5,
        tzinfo=timezone.utc,
    )

    create_transaction(
        user_id=test_user.id,
        account_id=test_account.id,
        category_id=income_category.id,
        amount="50000.00",
        transaction_date=transaction_date,
        description="Salary",
    )
    create_transaction(
        user_id=test_user.id,
        account_id=test_account.id,
        category_id=expense_category.id,
        amount="40000.00",
        transaction_date=transaction_date,
        description="Food",
    )


def allocation_payload(
    allocation_type="emergency_fund",
    amount="5000.00",
    name="Emergency Fund",
    current_value=None,
):
    payload = {
        "allocation_type": allocation_type,
        "amount": amount,
        "month": TEST_MONTH,
        "year": TEST_YEAR,
        "name": name,
        "notes": "September allocation",
    }

    if current_value is not None:
        payload["current_value"] = current_value

    return payload


def test_create_emergency_fund_allocation(
    client,
    seeded_monthly_savings,
):
    response = client.post(
        "/api/v1/savings-allocations",
        json=allocation_payload(),
    )

    assert response.status_code == 201

    body = response.json()

    assert body["id"] is not None
    assert body["allocation_type"] == "emergency_fund"
    assert body["amount"] == "5000.00"
    assert body["current_value"] is None
    assert body["gain_loss"] is None
    assert body["return_percentage"] is None


def test_create_investment_allocation(
    client,
    seeded_monthly_savings,
):
    response = client.post(
        "/api/v1/savings-allocations",
        json=allocation_payload(
            allocation_type="investment",
            amount="3000.00",
            name="Index Fund",
            current_value="3250.00",
        ),
    )

    assert response.status_code == 201

    body = response.json()

    assert body["allocation_type"] == "investment"
    assert body["amount"] == "3000.00"
    assert body["current_value"] == "3250.00"


def test_get_allocations(
    client,
    seeded_monthly_savings,
):
    client.post(
        "/api/v1/savings-allocations",
        json=allocation_payload(),
    )
    client.post(
        "/api/v1/savings-allocations",
        json=allocation_payload(
            allocation_type="investment",
            amount="3000.00",
            name="Index Fund",
        ),
    )

    response = client.get("/api/v1/savings-allocations")

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 2
    assert {item["allocation_type"] for item in body} == {
        "emergency_fund",
        "investment",
    }


def test_get_one_allocation(
    client,
    seeded_monthly_savings,
):
    created = client.post(
        "/api/v1/savings-allocations",
        json=allocation_payload(),
    )

    allocation_id = created.json()["id"]

    response = client.get(
        f"/api/v1/savings-allocations/{allocation_id}",
    )

    assert response.status_code == 200
    assert response.json()["id"] == allocation_id


def test_update_allocation(
    client,
    seeded_monthly_savings,
):
    created = client.post(
        "/api/v1/savings-allocations",
        json=allocation_payload(),
    )

    allocation_id = created.json()["id"]

    response = client.patch(
        f"/api/v1/savings-allocations/{allocation_id}",
        json={
            "amount": "6000.00",
            "name": "Updated Emergency Fund",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["amount"] == "6000.00"
    assert body["name"] == "Updated Emergency Fund"


def test_update_allocation_rejects_over_allocation_without_double_counting(
    client,
    seeded_monthly_savings,
):
    first = client.post(
        "/api/v1/savings-allocations",
        json=allocation_payload(
            amount="4000.00",
            name="Allocation A",
        ),
    )
    second = client.post(
        "/api/v1/savings-allocations",
        json=allocation_payload(
            allocation_type="investment",
            amount="3000.00",
            name="Allocation B",
        ),
    )

    assert first.status_code == 201
    assert second.status_code == 201

    allocation_id = first.json()["id"]

    response = client.patch(
        f"/api/v1/savings-allocations/{allocation_id}",
        json={
            "amount": "8000.00",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Allocation exceeds available savings for this month."
    )


def test_delete_allocation(
    client,
    seeded_monthly_savings,
):
    created = client.post(
        "/api/v1/savings-allocations",
        json=allocation_payload(),
    )

    allocation_id = created.json()["id"]

    delete_response = client.delete(
        f"/api/v1/savings-allocations/{allocation_id}",
    )

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    get_response = client.get(
        f"/api/v1/savings-allocations/{allocation_id}",
    )

    assert get_response.status_code == 404


def test_investment_gain_calculation(
    client,
    seeded_monthly_savings,
):
    response = client.post(
        "/api/v1/savings-allocations",
        json=allocation_payload(
            allocation_type="investment",
            amount="3000.00",
            name="Index Fund",
            current_value="3250.00",
        ),
    )

    assert response.status_code == 201
    assert Decimal(response.json()["gain_loss"]) == Decimal("250.00")


def test_investment_return_percentage_calculation(
    client,
    seeded_monthly_savings,
):
    response = client.post(
        "/api/v1/savings-allocations",
        json=allocation_payload(
            allocation_type="investment",
            amount="3000.00",
            name="Index Fund",
            current_value="3250.00",
        ),
    )

    assert response.status_code == 201

    return_percentage = Decimal(response.json()["return_percentage"])

    assert return_percentage.quantize(Decimal("0.01")) == Decimal("8.33")


def test_cannot_access_another_users_allocation(
    db,
    test_user,
    test_user_2,
    seeded_monthly_savings,
):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: test_user

    with TestClient(app) as test_client:
        created = test_client.post(
            "/api/v1/savings-allocations",
            json=allocation_payload(),
        )

        assert created.status_code == 201
        allocation_id = created.json()["id"]

    app.dependency_overrides[get_current_user] = lambda: test_user_2

    with TestClient(app) as test_client:
        response = test_client.get(
            f"/api/v1/savings-allocations/{allocation_id}",
        )

        assert response.status_code == 404

    app.dependency_overrides.clear()


def test_invalid_amount_rejected(
    client,
    seeded_monthly_savings,
):
    response = client.post(
        "/api/v1/savings-allocations",
        json=allocation_payload(
            amount="0.00",
        ),
    )

    assert response.status_code == 422


def test_invalid_month_rejected(
    client,
    seeded_monthly_savings,
):
    payload = allocation_payload()
    payload["month"] = 13

    response = client.post(
        "/api/v1/savings-allocations",
        json=payload,
    )

    assert response.status_code == 422


def test_investment_current_value_update_works(
    client,
    seeded_monthly_savings,
):
    created = client.post(
        "/api/v1/savings-allocations",
        json=allocation_payload(
            allocation_type="investment",
            amount="3000.00",
            name="Index Fund",
        ),
    )

    allocation_id = created.json()["id"]

    response = client.patch(
        f"/api/v1/savings-allocations/{allocation_id}",
        json={
            "current_value": "3300.00",
        },
    )

    assert response.status_code == 200
    assert response.json()["current_value"] == "3300.00"
    assert Decimal(response.json()["gain_loss"]) == Decimal("300.00")


def test_non_investment_allocation_clears_current_value(
    client,
    seeded_monthly_savings,
):
    response = client.post(
        "/api/v1/savings-allocations",
        json=allocation_payload(
            allocation_type="other",
            amount="1000.00",
            name="Other",
            current_value="1500.00",
        ),
    )

    assert response.status_code == 201
    assert response.json()["current_value"] is None


def test_allocation_exceeding_available_savings_is_rejected(
    client,
    seeded_monthly_savings,
):
    response = client.post(
        "/api/v1/savings-allocations",
        json=allocation_payload(
            amount="10001.00",
        ),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Allocation exceeds available savings for this month."
    )


def test_summary_returns_monthly_savings_allocation_totals(
    client,
    seeded_monthly_savings,
):
    first = client.post(
        "/api/v1/savings-allocations",
        json=allocation_payload(
            amount="5000.00",
            name="Emergency Fund",
        ),
    )
    second = client.post(
        "/api/v1/savings-allocations",
        json=allocation_payload(
            allocation_type="investment",
            amount="3000.00",
            name="Index Fund",
        ),
    )

    assert first.status_code == 201
    assert second.status_code == 201

    response = client.get(
        f"/api/v1/savings-allocations/summary?month={TEST_MONTH}&year={TEST_YEAR}",
    )

    assert response.status_code == 200

    body = response.json()

    assert body["month"] == TEST_MONTH
    assert body["year"] == TEST_YEAR
    assert Decimal(body["total_savings"]) == Decimal("10000.00")
    assert Decimal(body["total_allocated"]) == Decimal("8000.00")
    assert Decimal(body["remaining_savings"]) == Decimal("2000.00")


def test_summary_returns_zero_allocated_when_no_allocations(
    client,
    seeded_monthly_savings,
):
    response = client.get(
        f"/api/v1/savings-allocations/summary?month={TEST_MONTH}&year={TEST_YEAR}",
    )

    assert response.status_code == 200

    body = response.json()

    assert Decimal(body["total_savings"]) == Decimal("10000.00")
    assert Decimal(body["total_allocated"]) == Decimal("0")
    assert Decimal(body["remaining_savings"]) == Decimal("10000.00")


def test_summary_is_scoped_to_current_user(
    db,
    test_user,
    test_user_2,
    test_account,
    test_user_2_account,
    seeded_monthly_savings,
    create_transaction,
):
    other_income_category = Category(
        user_id=test_user_2.id,
        name="Other Salary",
        type=CategoryType.INCOME,
        icon="salary",
        color="#000000",
        is_default=False,
    )
    other_expense_category = Category(
        user_id=test_user_2.id,
        name="Other Food",
        type=CategoryType.EXPENSE,
        icon="food",
        color="#000000",
        is_default=False,
    )

    db.add(other_income_category)
    db.add(other_expense_category)
    db.commit()
    db.refresh(other_income_category)
    db.refresh(other_expense_category)

    transaction_date = datetime(
        TEST_YEAR,
        TEST_MONTH,
        5,
        tzinfo=timezone.utc,
    )

    create_transaction(
        user_id=test_user_2.id,
        account_id=test_user_2_account.id,
        category_id=other_income_category.id,
        amount="20000.00",
        transaction_date=transaction_date,
        description="Other Salary",
    )
    create_transaction(
        user_id=test_user_2.id,
        account_id=test_user_2_account.id,
        category_id=other_expense_category.id,
        amount="5000.00",
        transaction_date=transaction_date,
        description="Other Food",
    )

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: test_user

    with TestClient(app) as test_client:
        created = test_client.post(
            "/api/v1/savings-allocations",
            json=allocation_payload(
                amount="5000.00",
            ),
        )

        assert created.status_code == 201

    app.dependency_overrides[get_current_user] = lambda: test_user_2

    try:
        with TestClient(app) as test_client:
            response = test_client.get(
                f"/api/v1/savings-allocations/summary?month={TEST_MONTH}&year={TEST_YEAR}",
            )

            assert response.status_code == 200

            body = response.json()

            assert Decimal(body["total_savings"]) == Decimal("15000.00")
            assert Decimal(body["total_allocated"]) == Decimal("0")
            assert Decimal(body["remaining_savings"]) == Decimal("15000.00")

    finally:
        app.dependency_overrides.clear()


def test_summary_rejects_invalid_month(
    client,
):
    response = client.get(
        f"/api/v1/savings-allocations/summary?month=13&year={TEST_YEAR}",
    )

    assert response.status_code == 422


def test_savings_allocation_does_not_create_transaction_or_change_account_balance(
    client,
    db,
    test_account,
    seeded_monthly_savings,
):
    transaction_count_before = len(test_account.transactions)
    opening_balance_before = test_account.opening_balance

    response = client.post(
        "/api/v1/savings-allocations",
        json=allocation_payload(
            allocation_type="investment",
            amount="3000.00",
            name="Index Fund",
        ),
    )

    assert response.status_code == 201

    db.refresh(test_account)

    assert len(test_account.transactions) == transaction_count_before
    assert test_account.opening_balance == opening_balance_before
