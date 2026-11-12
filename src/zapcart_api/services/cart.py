from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from zapcart_api.models import Cart
from zapcart_api.repositories import CartRepository, ProductRepository
from zapcart_api.schemas import (
    CartItemAdd,
    CartItemResponse,
    CartProductSummary,
    CartResponse,
)

class CartService:
    def __init__(self, db: Session) -> None:
        self.cart_repo = CartRepository(db)
        self.product_repo = ProductRepository(db)

    def _build_cart_response(self, cart: Cart) -> CartResponse:
        item_responses: list[CartItemResponse] = []
        total_items = 0
        total_price = Decimal("0.00")

        for item in cart.items:
            product = item.product
            product_price = product.price if product else Decimal("0.00")
            subtotal = product_price * item.quantity
            total_items += item.quantity
            total_price += subtotal

            product_summary = None
            if product:
                product_summary = CartProductSummary(
                    id=product.id,
                    name=product.name,
                    slug=product.slug,
                    price=product.price,
                    stock_quantity=product.stock_quantity,
                    image_url=product.image_url,
                    is_active=product.is_active,
                )

            item_responses.append(
                CartItemResponse(
                    id=item.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    product=product_summary,
                    subtotal=subtotal,
                    created_at=item.created_at,
                    updated_at=item.updated_at,
                )
            )

        return CartResponse(
            id=cart.id,
            user_id=cart.user_id,
            items=item_responses,
            total_items=total_items,
            total_price=total_price,
            created_at=cart.created_at,
            updated_at=cart.updated_at,
        )

    def get_cart(self, user_id: int) -> CartResponse:
        cart = self.cart_repo.get_or_create_cart(user_id)
        return self._build_cart_response(cart)

    def add_item(self, user_id: int, item_in: CartItemAdd) -> CartResponse:
        cart = self.cart_repo.get_or_create_cart(user_id)
        product = self.product_repo.get_by_id(item_in.product_id, include_inactive=False)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found or inactive.",
            )

        existing_item = self.cart_repo.get_cart_item(cart.id, item_in.product_id)
        current_quantity = existing_item.quantity if existing_item else 0
        new_quantity = current_quantity + item_in.quantity

        if new_quantity > product.stock_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Requested quantity ({new_quantity}) exceeds available stock ({product.stock_quantity}).",
            )

        self.cart_repo.add_or_update_item(cart.id, item_in.product_id, item_in.quantity)
        refreshed_cart = self.cart_repo.get_by_user_id(user_id)
        return self._build_cart_response(refreshed_cart)

    def update_item_quantity(self, user_id: int, product_id: int, quantity: int) -> CartResponse:
        cart = self.cart_repo.get_or_create_cart(user_id)
        product = self.product_repo.get_by_id(product_id, include_inactive=False)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found or inactive.",
            )

        existing_item = self.cart_repo.get_cart_item(cart.id, product_id)
        if not existing_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found in cart.",
            )

        if quantity > product.stock_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Requested quantity ({quantity}) exceeds available stock ({product.stock_quantity}).",
            )

        self.cart_repo.update_item_quantity(cart.id, product_id, quantity)
        refreshed_cart = self.cart_repo.get_by_user_id(user_id)
        return self._build_cart_response(refreshed_cart)

    def remove_item(self, user_id: int, product_id: int) -> CartResponse:
        cart = self.cart_repo.get_or_create_cart(user_id)
        removed = self.cart_repo.remove_item(cart.id, product_id)
        if not removed:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found in cart.",
            )

        refreshed_cart = self.cart_repo.get_by_user_id(user_id)
        return self._build_cart_response(refreshed_cart)

    def clear_cart(self, user_id: int) -> None:
        cart = self.cart_repo.get_or_create_cart(user_id)
        self.cart_repo.clear_cart(cart.id)
