from jwt import InvalidTokenError

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.jwt import decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import TokenData


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
)

repository = UserRepository()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)

        user_id = payload.get("sub")

        email = payload.get("email")

        if user_id is None or email is None:
            raise credentials_exception

        token_data = TokenData(
            user_id=int(user_id),
            email=email,
        )

    except InvalidTokenError:
        raise credentials_exception

    user = repository.get_by_id(
        db,
        token_data.user_id,
    )

    if user is None:
        raise credentials_exception

    return user