from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["Health"])
def health():
    return {
        "status": "healthy",
        "service": "Afrab CFO Backend",
        "version": "0.1.0"
    }