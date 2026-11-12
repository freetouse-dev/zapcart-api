from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class CartItemAdd(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)

class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=1)

class CartProductSummary(BaseModel):
    id: int
    name: str
    slug: str
    price: Decimal
    stock_quantity: int
    image_url: Optional[str] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: Optional[CartProductSummary] = None
    subtotal: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CartResponse(BaseModel):
    id: int
    user_id: int
    items: list[CartItemResponse]
    total_items: int
    total_price: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
