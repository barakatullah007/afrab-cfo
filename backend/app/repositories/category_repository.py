from sqlalchemy.orm import Session

from app.models.category import Category


class CategoryRepository:

    def save(
        self,
        db: Session,
        category: Category,
    ) -> Category:
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    def get_all(
        self,
        db: Session,
        user_id: int,
    ) -> list[Category]:
        return (
            db.query(Category)
            .filter(Category.user_id == user_id)
            .order_by(Category.name.asc())
            .all()
        )

    def get_by_id(
        self,
        db: Session,
        category_id: int,
        user_id: int,
    ) -> Category | None:
        return (
            db.query(Category)
            .filter(
                Category.id == category_id,
                Category.user_id == user_id,
            )
            .first()
        )

    def get_by_name(
        self,
        db: Session,
        user_id: int,
        name: str,
    ) -> Category | None:
        return (
            db.query(Category)
            .filter(
                Category.user_id == user_id,
                Category.name == name,
            )
            .first()
        )

    def delete(
        self,
        db: Session,
        category: Category,
    ) -> None:
        db.delete(category)
        db.commit()