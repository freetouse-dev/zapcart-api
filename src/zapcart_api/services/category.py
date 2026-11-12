import re
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from zapcart_api.models import Category
from zapcart_api.repositories import CategoryRepository
from zapcart_api.schemas import CategoryCreate, CategoryUpdate

class CategoryService:
    def __init__(self, db: Session) -> None:
        self.category_repo = CategoryRepository(db)

    @staticmethod
    def _generate_slug(text: str) -> str:
        slug = re.sub(r"[^\w\s-]", "", text).strip().lower()
        return re.sub(r"[-\s]+", "-", slug)

    def create_category(self, category_in: CategoryCreate) -> Category:
        slug = category_in.slug or self._generate_slug(category_in.name)
        if self.category_repo.get_by_name(category_in.name, include_inactive=True):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists.",
            )
        if self.category_repo.get_by_slug(slug, include_inactive=True):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this slug already exists.",
            )
        return self.category_repo.create(
            name=category_in.name,
            slug=slug,
            is_active=True,
        )

    def get_category_by_id(self, category_id: int, include_inactive: bool = False) -> Category:
        category = self.category_repo.get_by_id(category_id, include_inactive=include_inactive)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found.",
            )
        return category

    def get_category_by_slug(self, slug: str, include_inactive: bool = False) -> Category:
        category = self.category_repo.get_by_slug(slug, include_inactive=include_inactive)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found.",
            )
        return category

    def list_categories(
        self,
        skip: int = 0,
        limit: int = 100,
        include_inactive: bool = False,
    ) -> list[Category]:
        return self.category_repo.list_categories(
            skip=skip,
            limit=limit,
            include_inactive=include_inactive,
        )

    def update_category(self, category_id: int, category_in: CategoryUpdate) -> Category:
        category = self.get_category_by_id(category_id, include_inactive=True)
        if category_in.name is not None and category_in.name != category.name:
            existing = self.category_repo.get_by_name(category_in.name, include_inactive=True)
            if existing and existing.id != category_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category with this name already exists.",
                )
        if category_in.slug is not None and category_in.slug != category.slug:
            existing = self.category_repo.get_by_slug(category_in.slug, include_inactive=True)
            if existing and existing.id != category_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category with this slug already exists.",
                )
        update_data = category_in.model_dump(exclude_unset=True)
        return self.category_repo.update(category, update_data)

    def delete_category(self, category_id: int) -> Category:
        category = self.get_category_by_id(category_id, include_inactive=True)
        if not category.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category is already inactive.",
            )
        return self.category_repo.soft_delete(category)

    def restore_category(self, category_id: int) -> Category:
        category = self.get_category_by_id(category_id, include_inactive=True)
        if category.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category is already active.",
            )
        return self.category_repo.restore(category)
