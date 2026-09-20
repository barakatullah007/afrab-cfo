from datetime import datetime, timezone
from decimal import Decimal

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


def goal_payload(
    name="Emergency Fund",
    target_amount="100000.00",
    current_amount="25000.00",
    priority="medium",
    status="active",
):
    return {
        "name": name,
        "description": "Six months of essential expenses",
        "target_amount": target_amount,
        "current_amount": current_amount,
        "target_date": "2027-08-02T00:00:00Z",
        "priority": priority,
        "status": status,
    }


def test_create_goal_success(
    db,
    test_user,
):
    client = create_client(db, test_user)

    try:
        response = client.post(
            "/api/v1/goals",
            json=goal_payload(),
        )

        assert response.status_code == 201

        body = response.json()

        assert body["id"] is not None
        assert body["name"] == "Emergency Fund"
        assert body["target_amount"] == "100000.00"
        assert body["current_amount"] == "25000.00"
        assert body["priority"] == "medium"
        assert body["status"] == "active"

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_create_goal_rejects_current_amount_above_target(
    db,
    test_user,
):
    client = create_client(db, test_user)

    try:
        response = client.post(
            "/api/v1/goals",
            json=goal_payload(
                target_amount="100000.00",
                current_amount="120000.00",
            ),
        )

        assert response.status_code == 422
        assert "Current amount cannot exceed target amount." in str(
            response.json()
        )

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_create_goal_rejects_zero_target_amount(
    db,
    test_user,
):
    client = create_client(db, test_user)

    try:
        response = client.post(
            "/api/v1/goals",
            json=goal_payload(
                target_amount="0.00",
            ),
        )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_create_goal_rejects_invalid_priority(
    db,
    test_user,
):
    client = create_client(db, test_user)

    try:
        response = client.post(
            "/api/v1/goals",
            json=goal_payload(
                priority="invalid",
            ),
        )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_create_goal_rejects_invalid_status(
    db,
    test_user,
):
    client = create_client(db, test_user)

    try:
        response = client.post(
            "/api/v1/goals",
            json=goal_payload(
                status="invalid",
            ),
        )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_get_goals_returns_current_users_goals(
    db,
    test_user,
):
    client = create_client(db, test_user)

    try:
        first = client.post(
            "/api/v1/goals",
            json=goal_payload(
                name="Emergency Fund",
            ),
        )

        second = client.post(
            "/api/v1/goals",
            json=goal_payload(
                name="Vacation",
                target_amount="50000.00",
            ),
        )

        assert first.status_code == 201
        assert second.status_code == 201

        response = client.get("/api/v1/goals")

        assert response.status_code == 200

        body = response.json()

        assert len(body) == 2
        assert {item["name"] for item in body} == {
            "Emergency Fund",
            "Vacation",
        }

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_get_goal_success(
    db,
    test_user,
):
    client = create_client(db, test_user)

    try:
        created = client.post(
            "/api/v1/goals",
            json=goal_payload(),
        )

        assert created.status_code == 201

        goal_id = created.json()["id"]

        response = client.get(
            f"/api/v1/goals/{goal_id}",
        )

        assert response.status_code == 200
        assert response.json()["id"] == goal_id
        assert response.json()["name"] == "Emergency Fund"

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_get_missing_goal_returns_404(
    db,
    test_user,
):
    client = create_client(db, test_user)

    try:
        response = client.get(
            "/api/v1/goals/999999",
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Goal not found"

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_update_goal_success(
    db,
    test_user,
):
    client = create_client(db, test_user)

    try:
        created = client.post(
            "/api/v1/goals",
            json=goal_payload(),
        )

        assert created.status_code == 201

        goal_id = created.json()["id"]

        response = client.put(
            f"/api/v1/goals/{goal_id}",
            json=goal_payload(
                name="Updated Emergency Fund",
                target_amount="150000.00",
                current_amount="50000.00",
                priority="high",
            ),
        )

        assert response.status_code == 200

        body = response.json()

        assert body["id"] == goal_id
        assert body["name"] == "Updated Emergency Fund"
        assert body["target_amount"] == "150000.00"
        assert body["current_amount"] == "50000.00"
        assert body["priority"] == "high"

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_update_missing_goal_returns_404(
    db,
    test_user,
):
    client = create_client(db, test_user)

    try:
        response = client.put(
            "/api/v1/goals/999999",
            json=goal_payload(
                name="Missing Goal",
            ),
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Goal not found"

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_delete_goal_success(
    db,
    test_user,
):
    client = create_client(db, test_user)

    try:
        created = client.post(
            "/api/v1/goals",
            json=goal_payload(),
        )

        assert created.status_code == 201

        goal_id = created.json()["id"]

        response = client.delete(
            f"/api/v1/goals/{goal_id}",
        )

        assert response.status_code == 204
        assert response.content == b""

        get_response = client.get(
            f"/api/v1/goals/{goal_id}",
        )

        assert get_response.status_code == 404

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_delete_missing_goal_returns_404(
    db,
    test_user,
):
    client = create_client(db, test_user)

    try:
        response = client.delete(
            "/api/v1/goals/999999",
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Goal not found"

    finally:
        app.dependency_overrides.clear()
        client.close()
        