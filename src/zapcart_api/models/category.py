from typing import TYPE_CHECKING
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from zapcart_api.database import Base
from zapcart_api.models.mixins import SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from zapcart_api.models.product import Product

class Category(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True, 
        autoincrement=True
    )
    name: Mapped[str] = mapped_column(
        String(100), 
        unique=True, 
        nullable=False
    )
    slug: Mapped[str] = mapped_column(
        String(120), 
        unique=True, 
        index=True, 
        nullable=False
    )

    products: Mapped[list["Product"]] = relationship("Product", back_populates="category")
