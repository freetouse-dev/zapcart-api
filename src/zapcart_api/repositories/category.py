from typing import Any, Optional
from sqlalchemy.orm import Session

from zapcart_api.models import Category

class CategoryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, category_id: int, include_inactive: bool = False) -> Optional[Category]:
        query = self.db.query(Category).filter(Category.id == category_id)
        if not include_inactive:
            query = query.filter(Category.is_active == True)
        return query.first()

    def get_by_slug(self, slug: str, include_inactive: bool = False) -> Optional[Category]:
        query = self.db.query(Category).filter(Category.slug == slug)
        if not include_inactive:
            query = query.filter(Category.is_active == True)
        return query.first()

    def get_by_name(self, name: str, include_inactive: bool = False) -> Optional[Category]:
        query = self.db.query(Category).filter(Category.name == name)
        if not include_inactive:
            query = query.filter(Category.is_active == True)
        return query.first()

    def list_categories(
        self,
        skip: int = 0,
        limit: int = 100,
        include_inactive: bool = False,
    ) -> list[Category]:
        query = self.db.query(Category)
        if not include_inactive:
            query = query.filter(Category.is_active == True)
        return query.offset(skip).limit(limit).all()

    def create(
        self,
        name: str,
        slug: str,
        is_active: bool = True,
    ) -> Category:
        new_category = Category(
            name=name,
            slug=slug,
            is_active=is_active,
        )
        self.db.add(new_category)
        self.db.commit()
        self.db.refresh(new_category)
        return new_category

    def update(self, category: Category, update_data: dict[str, Any]) -> Category:
        for field, value in update_data.items():
            if hasattr(category, field):
                setattr(category, field, value)
        self.db.commit()
        self.db.refresh(category)
        return category

    def soft_delete(self, category: Category) -> Category:
        category.soft_delete()
        self.db.commit()
        self.db.refresh(category)
        return category

    def restore(self, category: Category) -> Category:
        category.restore()
        self.db.commit()
        self.db.refresh(category)
        return category
