from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.session import get_db
from app.dependencies.ai import get_ai_conversation_service
from app.models.user import User
from app.schemas.ai import AIChatRequest, AIChatResponse
from app.services.ai_conversation_service import AIConversationService

router = APIRouter(
    prefix="/ai",
    tags=["AI Conversation"],
)


@router.post(
    "/chat",
    response_model=AIChatResponse,
)
def chat(
    request: AIChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: AIConversationService = Depends(
        get_ai_conversation_service
    ),
):
    return service.chat(
        db,
        current_user,
        request,
    )
