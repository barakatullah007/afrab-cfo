from fastapi import FastAPI

from app.api.v1.accounts import router as account_router
from app.api.v1.ai import router as ai_router
from app.api.v1.auth import router as auth_router
from app.api.v1.budgets import router as budget_router
from app.api.v1.categories import router as category_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.financial_intelligence import (
    router as financial_intelligence_router,
)
from app.api.v1.transfers import router as transfer_router
from app.api.v1.goals import router as goal_router
from app.api.v1.health import router as health_router
from app.api.v1.recurring_transactions import (
    router as recurring_transaction_router,
)
from app.api.v1.savings_allocations import (
    router as savings_allocation_router,
)
from app.api.v1.transactions import router as transaction_router
from app.core.config import settings
from app.api.v1.memory import router as memory_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-native Personal CFO Backend",
)

app.include_router(
    health_router,
    prefix="/api/v1",
)

app.include_router(
    auth_router,
    prefix="/api/v1",
)

app.include_router(
    ai_router,
    prefix="/api/v1",
)

app.include_router(
    account_router,
    prefix="/api/v1",
)

app.include_router(
    category_router,
    prefix="/api/v1",
)

app.include_router(
    transaction_router,
    prefix="/api/v1",
)

app.include_router(
    transfer_router,
    prefix="/api/v1",
)

app.include_router(
    budget_router,
    prefix="/api/v1",
)

app.include_router(
    goal_router,
    prefix="/api/v1",
)

app.include_router(
    recurring_transaction_router,
    prefix="/api/v1",
)

app.include_router(
    savings_allocation_router,
    prefix="/api/v1",
)

app.include_router(
    financial_intelligence_router,
    prefix="/api/v1",
)

app.include_router(
    dashboard_router,
    prefix="/api/v1",
)

app.include_router(
    memory_router,
    prefix="/api/v1",
)
