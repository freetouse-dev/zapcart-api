from fastapi import APIRouter, Depends, status

from zapcart_api.api.deps import get_cart_service, require_customer
from zapcart_api.models import User
from zapcart_api.schemas import (
    CartItemAdd,
    CartItemUpdate,
    CartResponse,
    MessageResponse,
)
from zapcart_api.services import CartService

router = APIRouter(prefix="/cart", tags=["Cart"])

@router.get(
    "/",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current customer cart",
)
def get_cart(
    current_user: User = Depends(require_customer),
    cart_service: CartService = Depends(get_cart_service),
) -> CartResponse:
    return cart_service.get_cart(current_user.id)

@router.post(
    "/items",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
    summary="Add product to cart (or increment quantity)",
)
def add_cart_item(
    item_in: CartItemAdd,
    current_user: User = Depends(require_customer),
    cart_service: CartService = Depends(get_cart_service),
) -> CartResponse:
    return cart_service.add_item(current_user.id, item_in)

@router.put(
    "/items/{product_id}",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
    summary="Update item quantity in cart",
)
def update_cart_item_quantity(
    product_id: int,
    item_in: CartItemUpdate,
    current_user: User = Depends(require_customer),
    cart_service: CartService = Depends(get_cart_service),
) -> CartResponse:
    return cart_service.update_item_quantity(current_user.id, product_id, item_in.quantity)

@router.delete(
    "/items/{product_id}",
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
    summary="Remove a product from cart",
)
def remove_cart_item(
    product_id: int,
    current_user: User = Depends(require_customer),
    cart_service: CartService = Depends(get_cart_service),
) -> CartResponse:
    return cart_service.remove_item(current_user.id, product_id)

@router.delete(
    "/items",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Clear all items from cart",
)
def clear_cart(
    current_user: User = Depends(require_customer),
    cart_service: CartService = Depends(get_cart_service),
) -> MessageResponse:
    cart_service.clear_cart(current_user.id)
    return MessageResponse(message="Cart cleared successfully.")
