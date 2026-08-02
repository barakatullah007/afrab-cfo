from fastapi import FastAPI

from app.api.v1.health import router as health_router
from app.core.config import settings
from app.api.v1.transactions import router as transaction_router
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
    transaction_router,
    prefix="/api/v1",
)