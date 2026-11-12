from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from zapcart_api.database import Base
from zapcart_api.models.mixins import SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from zapcart_api.models.category import Category

class Product(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True, 
        autoincrement=True
    )
    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(200), 
        nullable=False
    )
    slug: Mapped[str] = mapped_column(
        String(220), 
        unique=True, 
        index=True, 
        nullable=False
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), 
        nullable=False
    )
    stock_quantity: Mapped[int] = mapped_column(
        Integer, 
        default=0, 
        nullable=False
    )
    image_url: Mapped[Optional[str]] = mapped_column(
        String(500), 
        nullable=True
    )

    category: Mapped["Category"] = relationship("Category", back_populates="products")
