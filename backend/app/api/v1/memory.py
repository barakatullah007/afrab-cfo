from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.conversation_memory import ConversationMemoryResponse
from app.services.conversation_memory_service import ConversationMemoryService
from app.schemas.conversation_memory import ConversationMemoryCreate
from app.schemas.user import MessageResponse


router = APIRouter(
    prefix="/memory",
    tags=["Memory"],
)


@router.get("/", response_model=List[ConversationMemoryResponse])
def get_memory(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: ConversationMemoryService = Depends(ConversationMemoryService),
):
    recent = service.get_recent(db, current_user.id)
    return recent


@router.delete("/", response_model=MessageResponse)
def clear_memory(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: ConversationMemoryService = Depends(ConversationMemoryService),
):
    service.clear_user_memory(db, current_user.id)
    return {"message": "Memory cleared."}


@router.get("/preferences", response_model=List[ConversationMemoryResponse])
def get_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: ConversationMemoryService = Depends(ConversationMemoryService),
):
    prefs = service.get_preferences(db, current_user.id)
    return prefs
