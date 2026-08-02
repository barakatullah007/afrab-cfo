from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.user import User
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
)


class CategoryService:

    def __init__(self):
        self.repository = CategoryRepository()

    def create_category(
        self,
        db: Session,
        current_user: User,
        category_data: CategoryCreate,
    ) -> Category:

        existing = self.repository.get_by_name(
            db,
            current_user.id,
            category_data.name,
        )

        if existing:
            raise ValueError("Category already exists.")

        category = Category(
            user_id=current_user.id,
            name=category_data.name,
            type=category_data.type,
            icon=category_data.icon,
            color=category_data.color,
            is_default=False,
        )

        return self.repository.save(
            db,
            category,
        )

    def get_categories(
        self,
        db: Session,
        current_user: User,
    ) -> list[Category]:
        return self.repository.get_all(
            db,
            current_user.id,
        )

    def update_category(
        self,
        db: Session,
        category_id: int,
        current_user: User,
        category_data: CategoryUpdate,
    ) -> Category | None:

        category = self.repository.get_by_id(
            db,
            category_id,
            current_user.id,
        )

        if category is None:
            return None

        existing = self.repository.get_by_name(
            db,
            current_user.id,
            category_data.name,
        )

        if existing is not None and existing.id != category.id:
            raise ValueError(
                "Category already exists."
            )

        category.name = category_data.name
        category.icon = category_data.icon
        category.color = category_data.color

        return self.repository.save(
            db,
            category,
        )
    def delete_category(
        self,
        db: Session,
        category_id: int,
        current_user: User,
    ) -> Category | None:

        category = self.repository.get_by_id(
            db,
            category_id,
            current_user.id,
        )

        if category is None:
            return None

        if category.is_default:
            raise ValueError(
                "Default categories cannot be deleted."
            )

        self.repository.delete(
            db,
            category,
        )

        return category
