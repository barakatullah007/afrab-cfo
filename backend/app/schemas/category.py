from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.enums.category import CategoryType


class CategoryCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
        examples=["Food"],
    )

    type: CategoryType

    icon: str = Field(
        examples=["fa-solid fa-utensils"],
    )

    color: str = Field(
        examples=["#EF4444"],
    )


class CategoryUpdate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
    )

    icon: str

    color: str


class CategoryResponse(BaseModel):
    id: int
    name: str
    type: CategoryType
    icon: str
    color: str
    is_default: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )