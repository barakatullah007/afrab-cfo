from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.core.auth import get_current_user
from app.db.session import get_db
from app.dependencies.ai import get_ai_conversation_service
from app.main import app
from app.schemas.ai import AIChatResponse


def create_client(db, user, ai_service):
    def override_get_db():
        yield db

    def override_get_current_user():
        return user

    def override_get_ai_service():
        return ai_service

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[
        get_ai_conversation_service
    ] = override_get_ai_service

    return TestClient(app)


class FakeAIConversationService:
    def __init__(
        self,
        intent="financial_summary",
        answer="Your financial summary is available.",
        tool_used="financial_summary",
        confidence="high",
    ):
        self.intent = intent
        self.answer = answer
        self.tool_used = tool_used
        self.confidence = confidence
        self.last_request = None
        self.last_user = None

    def chat(
        self,
        db,
        current_user,
        request,
    ):
        self.last_request = request
        self.last_user = current_user

        return AIChatResponse(
            intent=self.intent,
            tool_used=self.tool_used,
            answer=self.answer,
            tool_output={
                "status": "test",
            },
            confidence=self.confidence,
            provider="test",
            model="fake-model",
            planning_steps=[
                self.intent,
            ],
            tools_executed=[
                self.tool_used,
            ]
            if self.tool_used
            else [],
            advisors_used=[],
            execution_time_ms=1,
            sources=[],
        )


def test_ai_chat_returns_structured_response(
    db,
    test_user,
):
    fake_service = FakeAIConversationService()

    client = create_client(
        db,
        test_user,
        fake_service,
    )

    try:
        response = client.post(
            "/api/v1/ai/chat",
            json={
                "message": "Show me my financial summary",
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["intent"] == "financial_summary"
        assert body["tool_used"] == "financial_summary"
        assert body["answer"] == (
            "Your financial summary is available."
        )
        assert body["confidence"] == "high"
        assert body["provider"] == "test"
        assert body["model"] == "fake-model"
        assert body["planning_steps"] == [
            "financial_summary",
        ]
        assert body["tools_executed"] == [
            "financial_summary",
        ]

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_ai_chat_passes_user_message_to_service(
    db,
    test_user,
):
    fake_service = FakeAIConversationService()

    client = create_client(
        db,
        test_user,
        fake_service,
    )

    try:
        message = "How much did I spend on food?"

        response = client.post(
            "/api/v1/ai/chat",
            json={
                "message": message,
            },
        )

        assert response.status_code == 200

        assert fake_service.last_request is not None
        assert fake_service.last_request.message == message
        assert fake_service.last_user.id == test_user.id

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_ai_chat_rejects_empty_message(
    db,
    test_user,
):
    fake_service = FakeAIConversationService()

    client = create_client(
        db,
        test_user,
        fake_service,
    )

    try:
        response = client.post(
            "/api/v1/ai/chat",
            json={
                "message": "",
            },
        )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_ai_chat_rejects_message_over_2000_characters(
    db,
    test_user,
):
    fake_service = FakeAIConversationService()

    client = create_client(
        db,
        test_user,
        fake_service,
    )

    try:
        response = client.post(
            "/api/v1/ai/chat",
            json={
                "message": "x" * 2001,
            },
        )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.clear()
        client.close()


@pytest.mark.parametrize(
    "intent,tool_used,message",
    [
        (
            "financial_summary",
            "financial_summary",
            "Show my financial summary",
        ),
        (
            "budget_utilization",
            "budget_utilization",
            "How am I doing against my budget?",
        ),
        (
            "goal_progress",
            "goal_progress",
            "How are my goals progressing?",
        ),
        (
            "cash_flow",
            "cash_flow",
            "Show my cash flow",
        ),
        (
            "category_insights",
            "category_insights",
            "Where am I spending money?",
        ),
        (
            "dashboard",
            "dashboard",
            "Show my dashboard",
        ),
        (
            "accounts",
            "accounts",
            "Show my accounts",
        ),
        (
            "transactions",
            "transactions",
            "Show my transactions",
        ),
    ],
)
def test_ai_chat_supports_structured_intents(
    db,
    test_user,
    intent,
    tool_used,
    message,
):
    fake_service = FakeAIConversationService(
        intent=intent,
        answer=f"Test response for {intent}.",
        tool_used=tool_used,
    )

    client = create_client(
        db,
        test_user,
        fake_service,
    )

    try:
        response = client.post(
            "/api/v1/ai/chat",
            json={
                "message": message,
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["intent"] == intent
        assert body["tool_used"] == tool_used
        assert body["answer"] == (
            f"Test response for {intent}."
        )

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_ai_chat_supports_help_intent(
    db,
    test_user,
):
    fake_service = FakeAIConversationService(
        intent="help",
        tool_used=None,
        answer="I can help with your finances.",
    )

    client = create_client(
        db,
        test_user,
        fake_service,
    )

    try:
        response = client.post(
            "/api/v1/ai/chat",
            json={
                "message": "What can you help me with?",
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["intent"] == "help"
        assert body["tool_used"] is None
        assert body["answer"] == (
            "I can help with your finances."
        )

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_ai_chat_supports_unknown_intent(
    db,
    test_user,
):
    fake_service = FakeAIConversationService(
        intent="unknown",
        tool_used=None,
        answer="I could not determine your request.",
        confidence="low",
    )

    client = create_client(
        db,
        test_user,
        fake_service,
    )

    try:
        response = client.post(
            "/api/v1/ai/chat",
            json={
                "message": "Tell me something completely unrelated.",
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["intent"] == "unknown"
        assert body["tool_used"] is None
        assert body["confidence"] == "low"

    finally:
        app.dependency_overrides.clear()
        client.close()


def test_ai_chat_response_contains_expected_metadata(
    db,
    test_user,
):
    fake_service = FakeAIConversationService()

    client = create_client(
        db,
        test_user,
        fake_service,
    )

    try:
        response = client.post(
            "/api/v1/ai/chat",
            json={
                "message": "Show my dashboard",
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert "intent" in body
        assert "tool_used" in body
        assert "answer" in body
        assert "tool_output" in body
        assert "confidence" in body
        assert "provider" in body
        assert "model" in body
        assert "planning_steps" in body
        assert "tools_executed" in body
        assert "advisors_used" in body
        assert "execution_time_ms" in body
        assert "sources" in body

        assert isinstance(
            body["planning_steps"],
            list,
        )

        assert isinstance(
            body["tools_executed"],
            list,
        )

        assert isinstance(
            body["advisors_used"],
            list,
        )

        assert isinstance(
            body["sources"],
            list,
        )

    finally:
        app.dependency_overrides.clear()
        client.close()