from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserRegister


class UserService:

    def __init__(self):
        self.repository = UserRepository()

    def get_by_email(
        self,
        db: Session,
        email: str,
    ) -> User | None:
        return self.repository.get_by_email(db, email)

    def get_by_google_id(
        self,
        db: Session,
        google_id: str,
    ) -> User | None:
        return self.repository.get_by_google_id(db, google_id)

    def create_user(
        self,
        db: Session,
        user_data: UserRegister,
        password_hash: str,
    ) -> User:

        user = User(
            name=user_data.name,
            email=user_data.email,
            password_hash=password_hash,
            auth_provider="local",
        )

        return self.repository.create(db, user)

    def create_google_user(
        self,
        db: Session,
        *,
        name: str,
        email: str,
        google_id: str,
        profile_picture: str | None = None,
    ) -> User:

        user = User(
            name=name,
            email=email,
            password_hash=None,
            auth_provider="google",
            google_id=google_id,
            profile_picture=profile_picture,
        )

        return self.repository.create(db, user)