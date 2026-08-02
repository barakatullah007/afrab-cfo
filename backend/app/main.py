from fastapi import FastAPI

from app.api.v1.accounts import router as account_router
from app.api.v1.auth import router as auth_router
from app.api.v1.categories import router as category_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.health import router as health_router
from app.api.v1.transactions import router as transaction_router
from app.core.config import settings

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
    dashboard_router,
    prefix="/api/v1",
)