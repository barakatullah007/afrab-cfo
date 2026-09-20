from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.core.auth import get_current_user
from app.db.session import get_db
from app.main import app
from app.models.conversation_memory import ConversationMemory


def create_client(db, user):
    def override_get_db():
        yield db

    def override_get_current_user():
        return user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    return TestClient(app)


def create_memory(
    db,
    user_id,
    message="Test memory",
    role="user",
    summary=None,
    memory_type="SHORT_TERM",
    session_id="test-session",
):
    memory = ConversationMemory(
        user_id=user_id,
        session_id=session_id,
        role=role,
        message=message,
        summary=summary,
        memory_type=memory_type,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    db.add(memory)
    db.commit()
    db.refresh(memory)

    return memory


def test_get_memory_returns_empty_list_for_new_user(db, test_user):
    client = create_client(db, test_user)

    try:
        response = client.get(
            "/api/v1/memory/",
        )

        assert response.status_code == 200
        assert response.json() == []

    finally:
        app.dependency_overrides.clear()


def test_get_memory_returns_current_users_memory(db, test_user):
    memory = create_memory(
        db=db,
        user_id=test_user.id,
        message="I want to save more money.",
    )

    memory_id = memory.id

    client = create_client(db, test_user)

    try:
        response = client.get(
            "/api/v1/memory/",
        )

        assert response.status_code == 200

        body = response.json()

        assert len(body) == 1
        assert body[0]["id"] == memory_id
        assert body[0]["user_id"] == test_user.id
        assert body[0]["message"] == "I want to save more money."

    finally:
        app.dependency_overrides.clear()


def test_get_memory_is_user_scoped(
    db,
    test_user,
    test_user_2,
):
    own_memory = create_memory(
        db=db,
        user_id=test_user.id,
        message="My private memory",
    )

    create_memory(
        db=db,
        user_id=test_user_2.id,
        message="Other user's private memory",
    )

    own_memory_id = own_memory.id

    client = create_client(db, test_user)

    try:
        response = client.get(
            "/api/v1/memory/",
        )

        assert response.status_code == 200

        body = response.json()

        assert len(body) == 1
        assert body[0]["id"] == own_memory_id
        assert body[0]["user_id"] == test_user.id
        assert body[0]["message"] == "My private memory"

    finally:
        app.dependency_overrides.clear()


def test_get_memory_returns_different_memory_types(
    db,
    test_user,
):
    short_term = create_memory(
        db=db,
        user_id=test_user.id,
        message="Short term memory",
        memory_type="SHORT_TERM",
    )

    preference = create_memory(
        db=db,
        user_id=test_user.id,
        message="User prefers conservative budgeting.",
        memory_type="PREFERENCE",
    )

    financial_context = create_memory(
        db=db,
        user_id=test_user.id,
        message="User has a monthly salary.",
        memory_type="FINANCIAL_CONTEXT",
    )

    short_term_id = short_term.id
    preference_id = preference.id
    financial_context_id = financial_context.id

    client = create_client(db, test_user)

    try:
        response = client.get(
            "/api/v1/memory/",
        )

        assert response.status_code == 200

        body = response.json()

        assert len(body) == 3

        returned_ids = {item["id"] for item in body}

        assert short_term_id in returned_ids
        assert preference_id in returned_ids
        assert financial_context_id in returned_ids

    finally:
        app.dependency_overrides.clear()


def test_get_preferences_returns_only_preferences(
    db,
    test_user,
):
    create_memory(
        db=db,
        user_id=test_user.id,
        message="Short term memory",
        memory_type="SHORT_TERM",
    )

    preference = create_memory(
        db=db,
        user_id=test_user.id,
        message="User prefers monthly budgeting.",
        memory_type="PREFERENCE",
    )

    preference_id = preference.id

    client = create_client(db, test_user)

    try:
        response = client.get(
            "/api/v1/memory/preferences",
        )

        assert response.status_code == 200

        body = response.json()

        assert len(body) == 1
        assert body[0]["id"] == preference_id
        assert body[0]["memory_type"] == "PREFERENCE"
        assert body[0]["message"] == "User prefers monthly budgeting."

    finally:
        app.dependency_overrides.clear()


def test_get_preferences_is_user_scoped(
    db,
    test_user,
    test_user_2,
):
    own_preference = create_memory(
        db=db,
        user_id=test_user.id,
        message="My preference",
        memory_type="PREFERENCE",
    )

    create_memory(
        db=db,
        user_id=test_user_2.id,
        message="Other user's preference",
        memory_type="PREFERENCE",
    )

    own_preference_id = own_preference.id

    client = create_client(db, test_user)

    try:
        response = client.get(
            "/api/v1/memory/preferences",
        )

        assert response.status_code == 200

        body = response.json()

        assert len(body) == 1
        assert body[0]["id"] == own_preference_id
        assert body[0]["user_id"] == test_user.id
        assert body[0]["message"] == "My preference"

    finally:
        app.dependency_overrides.clear()


def test_clear_memory_deletes_current_users_memory(
    db,
    test_user,
):
    memory = create_memory(
        db=db,
        user_id=test_user.id,
        message="Memory to delete",
    )

    memory_id = memory.id

    client = create_client(db, test_user)

    try:
        response = client.delete(
            "/api/v1/memory/",
        )

        assert response.status_code == 200

        body = response.json()

        assert body["message"] == "Memory cleared."

        deleted = (
            db.query(ConversationMemory)
            .filter(
                ConversationMemory.id == memory_id,
            )
            .first()
        )

        assert deleted is None

    finally:
        app.dependency_overrides.clear()


def test_clear_memory_does_not_delete_other_users_memory(
    db,
    test_user,
    test_user_2,
):
    own_memory = create_memory(
        db=db,
        user_id=test_user.id,
        message="My memory",
    )

    other_memory = create_memory(
        db=db,
        user_id=test_user_2.id,
        message="Other user's memory",
    )

    # Capture the IDs before expire_all().
    # The current user's row will be deleted by the API, so attempting
    # to access own_memory.id after expire_all() would raise
    # SQLAlchemy ObjectDeletedError.
    own_memory_id = own_memory.id
    other_memory_id = other_memory.id

    client = create_client(db, test_user)

    try:
        response = client.delete(
            "/api/v1/memory/",
        )

        assert response.status_code == 200

        db.expire_all()

        remaining = (
            db.query(ConversationMemory)
            .filter(
                ConversationMemory.id == other_memory_id,
            )
            .first()
        )

        deleted = (
            db.query(ConversationMemory)
            .filter(
                ConversationMemory.id == own_memory_id,
            )
            .first()
        )

        assert remaining is not None
        assert remaining.user_id == test_user_2.id
        assert remaining.message == "Other user's memory"

        assert deleted is None

    finally:
        app.dependency_overrides.clear()