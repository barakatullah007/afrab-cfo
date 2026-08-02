from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.jwt import create_access_token
from app.core.security import (
    hash_password,
    verify_password,
)
from app.db.session import get_db
from app.services.user_service import UserService
from app.schemas.user import (
    Token,
    UserLogin,
    UserRegister,
    UserResponse,
)
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

service = UserService()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db),
):
    existing_user = service.get_by_email(
        db,
        user_data.email,
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered.",
        )

    password_hash = hash_password(
        user_data.password
    )

    return service.create_user(
        db,
        user_data,
        password_hash,
    )
    
@router.post(
    "/login",
    response_model=Token,
)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    user = service.get_by_email(
        db,
        credentials.email,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if user.password_hash is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please login using Google.",
        )

    if not verify_password(
        credentials.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    access_token = create_access_token(
        user_id=user.id,
        email=user.email,
    )

    return Token(
        access_token=access_token,
    )