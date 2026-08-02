from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.session import get_db
from app.dependencies.services import get_financial_intelligence_service
from app.models.user import User
from app.schemas.financial_intelligence import (
    BudgetUtilizationInsight,
    CategoryInsight,
    FinancialIntelligenceSummary,
    GoalProgressInsight,
    MonthlyCashFlow,
)
from app.services.financial_intelligence_service import (
    FinancialIntelligenceService,
)

router = APIRouter(
    prefix="/financial-intelligence",
    tags=["Financial Intelligence"],
)


@router.get(
    "/summary",
    response_model=FinancialIntelligenceSummary,
)
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: FinancialIntelligenceService = Depends(
        get_financial_intelligence_service
    ),
):
    return service.get_summary(
        db,
        current_user,
    )


@router.get(
    "/budget-utilization",
    response_model=list[BudgetUtilizationInsight],
)
def get_budget_utilization(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: FinancialIntelligenceService = Depends(
        get_financial_intelligence_service
    ),
):
    return service.get_budget_utilization(
        db,
        current_user,
    )


@router.get(
    "/goal-progress",
    response_model=list[GoalProgressInsight],
)
def get_goal_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: FinancialIntelligenceService = Depends(
        get_financial_intelligence_service
    ),
):
    return service.get_goal_progress(
        db,
        current_user,
    )


@router.get(
    "/category-insights",
    response_model=list[CategoryInsight],
)
def get_category_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: FinancialIntelligenceService = Depends(
        get_financial_intelligence_service
    ),
):
    return service.get_category_insights(
        db,
        current_user,
    )


@router.get(
    "/monthly-cashflow",
    response_model=MonthlyCashFlow,
)
def get_monthly_cashflow(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    service: FinancialIntelligenceService = Depends(
        get_financial_intelligence_service
    ),
):
    return service.get_monthly_cashflow(
        db,
        current_user,
    )
