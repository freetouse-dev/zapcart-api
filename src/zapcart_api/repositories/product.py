from decimal import Decimal
from typing import Any, Optional
from sqlalchemy.orm import Session

from zapcart_api.models import Product

class ProductRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, product_id: int, include_inactive: bool = False) -> Optional[Product]:
        query = self.db.query(Product).filter(Product.id == product_id)
        if not include_inactive:
            query = query.filter(Product.is_active == True)
        return query.first()

    def get_by_slug(self, slug: str, include_inactive: bool = False) -> Optional[Product]:
        query = self.db.query(Product).filter(Product.slug == slug)
        if not include_inactive:
            query = query.filter(Product.is_active == True)
        return query.first()

    def list_products(
        self,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None,
        include_inactive: bool = False,
    ) -> list[Product]:
        query = self.db.query(Product)
        if category_id is not None:
            query = query.filter(Product.category_id == category_id)
        if not include_inactive:
            query = query.filter(Product.is_active == True)
        return query.offset(skip).limit(limit).all()

    def create(
        self,
        category_id: int,
        name: str,
        slug: str,
        price: Decimal,
        stock_quantity: int = 0,
        image_url: Optional[str] = None,
        is_active: bool = True,
    ) -> Product:
        new_product = Product(
            category_id=category_id,
            name=name,
            slug=slug,
            price=price,
            stock_quantity=stock_quantity,
            image_url=image_url,
            is_active=is_active,
        )
        self.db.add(new_product)
        self.db.commit()
        self.db.refresh(new_product)
        return new_product

    def update(self, product: Product, update_data: dict[str, Any]) -> Product:
        for field, value in update_data.items():
            if hasattr(product, field):
                setattr(product, field, value)
        self.db.commit()
        self.db.refresh(product)
        return product

    def soft_delete(self, product: Product) -> Product:
        product.soft_delete()
        self.db.commit()
        self.db.refresh(product)
        return product

    def restore(self, product: Product) -> Product:
        product.restore()
        self.db.commit()
        self.db.refresh(product)
        return product
