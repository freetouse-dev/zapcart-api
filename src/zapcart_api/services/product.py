import re
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from zapcart_api.models import Product
from zapcart_api.repositories import CategoryRepository, ProductRepository
from zapcart_api.schemas import ProductCreate, ProductUpdate

class ProductService:
    def __init__(self, db: Session) -> None:
        self.product_repo = ProductRepository(db)
        self.category_repo = CategoryRepository(db)

    @staticmethod
    def _generate_slug(text: str) -> str:
        slug = re.sub(r"[^\w\s-]", "", text).strip().lower()
        return re.sub(r"[-\s]+", "-", slug)

    def create_product(self, product_in: ProductCreate) -> Product:
        category = self.category_repo.get_by_id(product_in.category_id, include_inactive=False)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found or inactive.",
            )
        slug = product_in.slug or self._generate_slug(product_in.name)
        if self.product_repo.get_by_slug(slug, include_inactive=True):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product with this slug already exists.",
            )
        return self.product_repo.create(
            category_id=product_in.category_id,
            name=product_in.name,
            slug=slug,
            price=product_in.price,
            stock_quantity=product_in.stock_quantity,
            image_url=product_in.image_url,
            is_active=True,
        )

    def get_product_by_id(self, product_id: int, include_inactive: bool = False) -> Product:
        product = self.product_repo.get_by_id(product_id, include_inactive=include_inactive)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found.",
            )
        return product

    def get_product_by_slug(self, slug: str, include_inactive: bool = False) -> Product:
        product = self.product_repo.get_by_slug(slug, include_inactive=include_inactive)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found.",
            )
        return product

    def list_products(
        self,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None,
        include_inactive: bool = False,
    ) -> list[Product]:
        if category_id is not None:
            category = self.category_repo.get_by_id(category_id, include_inactive=include_inactive)
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Category not found.",
                )
        return self.product_repo.list_products(
            skip=skip,
            limit=limit,
            category_id=category_id,
            include_inactive=include_inactive,
        )

    def update_product(self, product_id: int, product_in: ProductUpdate) -> Product:
        product = self.get_product_by_id(product_id, include_inactive=True)
        if product_in.category_id is not None:
            category = self.category_repo.get_by_id(product_in.category_id, include_inactive=False)
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category not found or inactive.",
                )
        if product_in.slug is not None and product_in.slug != product.slug:
            existing = self.product_repo.get_by_slug(product_in.slug, include_inactive=True)
            if existing and existing.id != product_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Product with this slug already exists.",
                )
        update_data = product_in.model_dump(exclude_unset=True)
        return self.product_repo.update(product, update_data)

    def delete_product(self, product_id: int) -> Product:
        product = self.get_product_by_id(product_id, include_inactive=True)
        if not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product is already inactive.",
            )
        return self.product_repo.soft_delete(product)

    def restore_product(self, product_id: int) -> Product:
        product = self.get_product_by_id(product_id, include_inactive=True)
        if product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product is already active.",
            )
        return self.product_repo.restore(product)
