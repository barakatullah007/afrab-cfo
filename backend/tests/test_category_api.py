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


def category_payload(
    name="Travel",
    category_type="expense",
    icon="travel",
    color="#123456",
):
    return {
        "name": name,
        "type": category_type,
        "icon": icon,
        "color": color,
    }


def test_create_category_success(
    db,
    test_user,
):
    client = create_client(db, test_user)

    try:
        response = client.post(
            "/api/v1/categories",
            json=category_payload(),
        )

        assert response.status_code == 201

        body = response.json()

        assert body["id"] is not None
        assert body["name"] == "Travel"
        assert body["type"] == "expense"
        assert body["icon"] == "travel"
        assert body["color"] == "#123456"

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_create_income_category_success(
    db,
    test_user,
):
    client = create_client(db, test_user)

    try:
        response = client.post(
            "/api/v1/categories",
            json=category_payload(
                name="Salary",
                category_type="income",
                icon="salary",
            ),
        )

        assert response.status_code == 201

        body = response.json()

        assert body["name"] == "Salary"
        assert body["type"] == "income"

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_create_duplicate_category_returns_409(
    db,
    test_user,
    expense_category,
):
    client = create_client(db, test_user)

    try:
        response = client.post(
            "/api/v1/categories",
            json=category_payload(
                name=expense_category.name,
            ),
        )

        assert response.status_code == 409

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_get_categories_returns_current_users_categories(
    db,
    test_user,
    expense_category,
):
    client = create_client(db, test_user)

    try:
        response = client.get("/api/v1/categories")

        assert response.status_code == 200

        body = response.json()

        assert len(body) == 1
        assert body[0]["id"] == expense_category.id
        assert body[0]["name"] == expense_category.name

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_get_categories_is_user_scoped(
    db,
    test_user,
    test_user_2,
    expense_category,
):
    from app.enums.category import CategoryType
    from app.models.category import Category

    other_category = Category(
        user_id=test_user_2.id,
        name="Other User Category",
        type=CategoryType.EXPENSE,
        icon="other",
        color="#000000",
        is_default=False,
    )

    db.add(other_category)
    db.commit()

    client = create_client(db, test_user)

    try:
        response = client.get("/api/v1/categories")

        assert response.status_code == 200

        body = response.json()

        assert len(body) == 1
        assert body[0]["id"] == expense_category.id

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_update_category_success(
    db,
    test_user,
    expense_category,
):
    client = create_client(db, test_user)

    try:
        response = client.put(
            f"/api/v1/categories/{expense_category.id}",
            json=category_payload(
                name="Dining",
                icon="restaurant",
                color="#654321",
            ),
        )

        assert response.status_code == 200

        body = response.json()

        assert body["id"] == expense_category.id
        assert body["name"] == "Dining"
        assert body["icon"] == "restaurant"
        assert body["color"] == "#654321"

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_update_missing_category_returns_404(
    db,
    test_user,
):
    client = create_client(db, test_user)

    try:
        response = client.put(
            "/api/v1/categories/999999",
            json=category_payload(
                name="Missing",
            ),
        )

        assert response.status_code == 404

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_update_other_users_category_returns_404(
    db,
    test_user,
    test_user_2,
    expense_category,
):
    # Create a category belonging to another user.
    from app.enums.category import CategoryType
    from app.models.category import Category

    other_category = Category(
        user_id=test_user_2.id,
        name="Other User Category",
        type=CategoryType.EXPENSE,
        icon="other",
        color="#000000",
        is_default=False,
    )

    db.add(other_category)
    db.commit()
    db.refresh(other_category)

    client = create_client(db, test_user)

    try:
        response = client.put(
            f"/api/v1/categories/{other_category.id}",
            json=category_payload(
                name="Attempted Update",
            ),
        )

        assert response.status_code == 404

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_delete_category_success(
    db,
    test_user,
    expense_category,
):
    client = create_client(db, test_user)

    try:
        response = client.delete(
            f"/api/v1/categories/{expense_category.id}",
        )

        assert response.status_code == 204
        assert response.content == b""

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_delete_missing_category_returns_404(
    db,
    test_user,
):
    client = create_client(db, test_user)

    try:
        response = client.delete(
            "/api/v1/categories/999999",
        )

        assert response.status_code == 404

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_delete_other_users_category_returns_404(
    db,
    test_user,
    test_user_2,
):
    from app.enums.category import CategoryType
    from app.models.category import Category

    other_category = Category(
        user_id=test_user_2.id,
        name="Other User Category",
        type=CategoryType.EXPENSE,
        icon="other",
        color="#000000",
        is_default=False,
    )

    db.add(other_category)
    db.commit()
    db.refresh(other_category)

    client = create_client(db, test_user)

    try:
        response = client.delete(
            f"/api/v1/categories/{other_category.id}",
        )

        assert response.status_code == 404

    finally:
        app.dependency_overrides.clear()
        client.close()