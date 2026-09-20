from fastapi.testclient import TestClient

from app.core.security import hash_password
from app.db.session import get_db
from app.main import app
from app.models.user import User


def test_register_success(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "name": "New User",
                    "email": "new@example.com",
                    "password": "Password@123",
                },
            )

        assert response.status_code == 201

        body = response.json()

        assert body["name"] == "New User"
        assert body["email"] == "new@example.com"
        assert "password_hash" not in body

    finally:
        app.dependency_overrides.clear()


def test_register_duplicate_email_returns_409(db, test_user):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "name": "Another User",
                    "email": test_user.email,
                    "password": "Password@123",
                },
            )

        assert response.status_code == 409

    finally:
        app.dependency_overrides.clear()


def test_register_invalid_password_returns_422(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/auth/register",
                json={
                    "name": "New User",
                    "email": "new@example.com",
                    "password": "short",
                },
            )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.clear()


def test_login_success(db):
    user = User(
        name="Login User",
        email="login@example.com",
        password_hash=hash_password("Password@123"),
        auth_provider="local",
    )

    db.add(user)
    db.commit()

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/auth/login",
                data={
                    "username": "login@example.com",
                    "password": "Password@123",
                },
            )

        assert response.status_code == 200

        body = response.json()

        assert body["access_token"]
        assert body["token_type"] == "bearer"

    finally:
        app.dependency_overrides.clear()


def test_login_invalid_password_returns_401(db):
    user = User(
        name="Login User",
        email="login@example.com",
        password_hash=hash_password("Password@123"),
        auth_provider="local",
    )

    db.add(user)
    db.commit()

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/auth/login",
                data={
                    "username": "login@example.com",
                    "password": "WrongPassword@123",
                },
            )

        assert response.status_code == 401

    finally:
        app.dependency_overrides.clear()