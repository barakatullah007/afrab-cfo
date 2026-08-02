from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegister(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
        examples=["Abid Khan"],
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        examples=["Password@123"],
    )


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class GoogleLogin(BaseModel):
    id_token: str = Field(
        examples=["Google OAuth ID Token"],
    )


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    auth_provider: Literal[
        "local",
        "google",
    ]

    profile_picture: str | None = None

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class Token(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"


class TokenData(BaseModel):
    user_id: int
    email: EmailStr


class MessageResponse(BaseModel):
    message: str