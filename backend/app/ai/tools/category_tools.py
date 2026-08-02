from typing import Any

from sqlalchemy.orm import Session

from app.ai.tools._serialization import to_jsonable
from app.models.user import User
from app.services.category_service import CategoryService


def get_categories(
    db: Session,
    current_user: User,
    service: CategoryService,
) -> list[dict[str, Any]]:
    """Return categories owned by the authenticated user.

    Args:
        db: Database session.
        current_user: Authenticated user.
        service: Category business service.

    Returns:
        JSON-serializable category records.
    """

    return to_jsonable(
        service.get_categories(
            db,
            current_user,
        )
    )
