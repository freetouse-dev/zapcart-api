from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from zapcart_api.core.enums import OrderStatus
from zapcart_api.schemas.cart import CartProductSummary

class DirectBuyRequest(BaseModel):
    product_id: int = Field(..., description="ID of the product to purchase directly")
    quantity: int = Field(default=1, ge=1, description="Quantity to purchase")

class OrderStatusUpdate(BaseModel):
    status: OrderStatus

class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    product_id: int
    quantity: int
    price_at_purchase: Decimal
    product: Optional[CartProductSummary] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_price: Decimal
    status: OrderStatus
    items: list[OrderItemResponse]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
