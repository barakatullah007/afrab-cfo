from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.dashboard_recent import DashboardRecentTransaction
from app.schemas.dashboard_summary import DashboardSummary
from app.services.dashboard_service import DashboardService

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)

service = DashboardService()


@router.get(
    "/summary",
    response_model=DashboardSummary,
)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.get_summary(
        db,
        current_user,
    )


@router.get(
    "/recent-transactions",
    response_model=list[DashboardRecentTransaction],
)
def get_recent_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return service.get_recent_transactions(
        db,
        current_user,
    )