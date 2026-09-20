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


def test_dashboard_summary_returns_zero_values_for_new_user(
    db,
    test_user,
):
    client = create_client(db, test_user)

    try:
        response = client.get(
            "/api/v1/dashboard/summary",
        )

        assert response.status_code == 200

        body = response.json()

        assert body["total_balance"] in ("0", "0.00")
        assert body["monthly_income"] in ("0", "0.00")
        assert body["monthly_expense"] in ("0", "0.00")
        assert body["savings"] in ("0", "0.00")

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_dashboard_summary_returns_account_balance(
    db,
    test_user,
    test_account,
):
    client = create_client(db, test_user)

    try:
        response = client.get(
            "/api/v1/dashboard/summary",
        )

        assert response.status_code == 200

        body = response.json()

        assert body["total_balance"] == "10000.00"

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_dashboard_summary_calculates_income_expense_and_savings(
    db,
    test_user,
    test_account,
    income_category,
    expense_category,
    create_transaction,
):
    now = datetime.now(timezone.utc)

    create_transaction(
        user_id=test_user.id,
        account_id=test_account.id,
        category_id=income_category.id,
        amount="50000.00",
        transaction_date=now,
        description="Salary",
    )

    create_transaction(
        user_id=test_user.id,
        account_id=test_account.id,
        category_id=expense_category.id,
        amount="12000.00",
        transaction_date=now,
        description="Rent",
    )

    create_transaction(
        user_id=test_user.id,
        account_id=test_account.id,
        category_id=expense_category.id,
        amount="3000.00",
        transaction_date=now,
        description="Food",
    )

    client = create_client(db, test_user)

    try:
        response = client.get(
            "/api/v1/dashboard/summary",
        )

        assert response.status_code == 200

        body = response.json()

        # Current DashboardService calculates:
        # opening balance + income - expenses
        #
        # 10000 + 50000 - 12000 - 3000 = 45000
        assert body["total_balance"] == "45000.00"

        assert body["monthly_income"] == "50000.00"
        assert body["monthly_expense"] == "15000.00"
        assert body["savings"] == "35000.00"

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_dashboard_summary_is_user_scoped(
    db,
    test_user,
    test_user_2,
    test_account,
    test_user_2_account,
):
    client = create_client(db, test_user)

    try:
        response = client.get(
            "/api/v1/dashboard/summary",
        )

        assert response.status_code == 200

        body = response.json()

        assert body["total_balance"] == "10000.00"

        # Second user's account must not be included.
        assert body["total_balance"] != "30000.00"

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_dashboard_recent_transactions_returns_empty_list_for_new_user(
    db,
    test_user,
):
    client = create_client(db, test_user)

    try:
        response = client.get(
            "/api/v1/dashboard/recent-transactions",
        )

        assert response.status_code == 200
        assert response.json() == []

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_dashboard_recent_transactions_returns_transaction_details(
    db,
    test_user,
    test_account,
    expense_category,
    create_transaction,
):
    transaction_date = datetime.now(timezone.utc)

    create_transaction(
        user_id=test_user.id,
        account_id=test_account.id,
        category_id=expense_category.id,
        amount="750.00",
        transaction_date=transaction_date,
        description="Dinner",
    )

    client = create_client(db, test_user)

    try:
        response = client.get(
            "/api/v1/dashboard/recent-transactions",
        )

        assert response.status_code == 200

        body = response.json()

        assert len(body) == 1

        transaction = body[0]

        assert transaction["description"] == "Dinner"
        assert transaction["amount"] == "750.00"
        assert transaction["account_name"] == test_account.name
        assert transaction["category_name"] == expense_category.name
        assert transaction["id"] is not None

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_dashboard_recent_transactions_is_user_scoped(
    db,
    test_user,
    test_user_2,
    test_account,
    test_user_2_account,
    expense_category,
    create_transaction,
):
    create_transaction(
        user_id=test_user.id,
        account_id=test_account.id,
        category_id=expense_category.id,
        amount="500.00",
        description="My transaction",
    )

    from app.enums.category import CategoryType
    from app.models.category import Category

    other_category = Category(
        user_id=test_user_2.id,
        name="Other User Expense",
        type=CategoryType.EXPENSE,
        icon="other",
        color="#000000",
        is_default=False,
    )

    db.add(other_category)
    db.commit()
    db.refresh(other_category)

    create_transaction(
        user_id=test_user_2.id,
        account_id=test_user_2_account.id,
        category_id=other_category.id,
        amount="999.00",
        description="Other user transaction",
    )

    client = create_client(db, test_user)

    try:
        response = client.get(
            "/api/v1/dashboard/recent-transactions",
        )

        assert response.status_code == 200

        body = response.json()

        assert len(body) == 1
        assert body[0]["description"] == "My transaction"
        assert body[0]["amount"] == "500.00"

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_dashboard_recent_transactions_limits_to_ten(
    db,
    test_user,
    test_account,
    expense_category,
    create_transaction,
):
    for index in range(15):
        create_transaction(
            user_id=test_user.id,
            account_id=test_account.id,
            category_id=expense_category.id,
            amount=str(index + 1),
            description=f"Transaction {index + 1}",
        )

    client = create_client(db, test_user)

    try:
        response = client.get(
            "/api/v1/dashboard/recent-transactions",
        )

        assert response.status_code == 200

        body = response.json()

        assert len(body) == 10

    finally:
        app.dependency_overrides.clear()
        client.close()