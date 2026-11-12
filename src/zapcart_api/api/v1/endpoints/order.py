from typing import Optional
from fastapi import APIRouter, Depends, Query, status

from zapcart_api.api.deps import (
    get_current_user,
    get_order_service,
    require_admin,
    require_customer,
)
from zapcart_api.core.enums import OrderStatus
from zapcart_api.models import Order, User
from zapcart_api.schemas import (
    DirectBuyRequest,
    OrderResponse,
    OrderStatusUpdate,
)
from zapcart_api.services import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.get(
    "",
    response_model=list[OrderResponse],
    status_code=status.HTTP_200_OK,
    summary="List orders (Customer sees own, Admin sees all)",
)
def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status_filter: Optional[OrderStatus] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
) -> list[Order]:
    return order_service.list_orders(
        current_user=current_user,
        skip=skip,
        limit=limit,
        status_filter=status_filter,
    )

@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Get order by ID",
)
def get_order_by_id(
    order_id: int,
    current_user: User = Depends(get_current_user),
    order_service: OrderService = Depends(get_order_service),
) -> Order:
    return order_service.get_order_by_id(order_id, current_user)

@router.post(
    "/buy-now",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Buy a product directly (without cart)",
)
def buy_now(
    buy_in: DirectBuyRequest,
    current_user: User = Depends(require_customer),
    order_service: OrderService = Depends(get_order_service),
) -> Order:
    return order_service.create_direct_order(current_user.id, buy_in.product_id, buy_in.quantity)

@router.post(
    "/checkout-cart",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Checkout all items from cart",
)
def checkout_cart(
    current_user: User = Depends(require_customer),
    order_service: OrderService = Depends(get_order_service),
) -> Order:
    return order_service.create_order_from_cart(current_user.id)

@router.post(
    "/checkout-cart/{product_id}",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Checkout a single product item from cart",
)
def checkout_cart_item(
    product_id: int,
    current_user: User = Depends(require_customer),
    order_service: OrderService = Depends(get_order_service),
) -> Order:
    return order_service.create_order_from_cart_item(current_user.id, product_id)

@router.post(
    "/{order_id}/cancel",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Cancel own order (Customer only, while pending)",
)
def cancel_order(
    order_id: int,
    current_user: User = Depends(require_customer),
    order_service: OrderService = Depends(get_order_service),
) -> Order:
    return order_service.cancel_order_by_customer(order_id, current_user.id)

@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Update order status (Admin only; reduces stock when delivered)",
)
def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    admin_user: User = Depends(require_admin),
    order_service: OrderService = Depends(get_order_service),
) -> Order:
    return order_service.update_order_status_by_admin(order_id, status_update.status)
