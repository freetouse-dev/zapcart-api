from decimal import Decimal
from typing import Any, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from zapcart_api.core.enums import OrderStatus, UserRole
from zapcart_api.models import Order, User
from zapcart_api.repositories import (
    CartRepository,
    OrderRepository,
    ProductRepository,
)

class OrderService:
    def __init__(self, db: Session) -> None:
        self.order_repo = OrderRepository(db)
        self.cart_repo = CartRepository(db)
        self.product_repo = ProductRepository(db)

    def create_direct_order(self, user_id: int, product_id: int, quantity: int = 1) -> Order:
        product = self.product_repo.get_by_id(product_id, include_inactive=False)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found or inactive.",
            )
        if quantity > product.stock_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for '{product.name}' (available: {product.stock_quantity}, requested: {quantity}).",
            )
        items_data = [
            {
                "product_id": product.id,
                "quantity": quantity,
                "price_at_purchase": product.price,
            }
        ]
        total_price = product.price * quantity
        return self.order_repo.create_order(
            user_id=user_id,
            total_price=Decimal(str(total_price)),
            items_data=items_data,
        )

    def create_order_from_cart(self, user_id: int) -> Order:
        cart = self.cart_repo.get_by_user_id(user_id)
        if not cart or not cart.items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot create order from an empty cart.",
            )
        items_data: list[dict[str, Any]] = []
        for cart_item in cart.items:
            product = cart_item.product or self.product_repo.get_by_id(cart_item.product_id, include_inactive=False)
            if not product or not product.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A product in your cart is no longer available.",
                )
            if cart_item.quantity > product.stock_quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for '{product.name}' (available: {product.stock_quantity}, requested: {cart_item.quantity}).",
                )
            items_data.append(
                {
                    "product_id": product.id,
                    "quantity": cart_item.quantity,
                    "price_at_purchase": product.price,
                }
            )
        total_price = sum(item["quantity"] * item["price_at_purchase"] for item in items_data)
        order = self.order_repo.create_order(
            user_id=user_id,
            total_price=Decimal(str(total_price)),
            items_data=items_data,
        )
        self.cart_repo.clear_cart(cart.id)
        return order

    def create_order_from_cart_item(self, user_id: int, product_id: int) -> Order:
        cart = self.cart_repo.get_by_user_id(user_id)
        if not cart or not cart.items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Your cart is empty.",
            )
        cart_item = self.cart_repo.get_cart_item(cart.id, product_id)
        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found in your cart.",
            )
        product = cart_item.product or self.product_repo.get_by_id(product_id, include_inactive=False)
        if not product or not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This product is no longer available.",
            )
        if cart_item.quantity > product.stock_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for '{product.name}' (available: {product.stock_quantity}, requested: {cart_item.quantity}).",
            )
        items_data = [
            {
                "product_id": product.id,
                "quantity": cart_item.quantity,
                "price_at_purchase": product.price,
            }
        ]
        total_price = product.price * cart_item.quantity
        order = self.order_repo.create_order(
            user_id=user_id,
            total_price=Decimal(str(total_price)),
            items_data=items_data,
        )
        self.cart_repo.remove_item(cart.id, product_id)
        return order

    def get_order_by_id(self, order_id: int, current_user: User) -> Order:
        if current_user.role == UserRole.ADMIN:
            order = self.order_repo.get_by_id(order_id)
        else:
            order = self.order_repo.get_by_id_and_user_id(order_id, current_user.id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found.",
            )
        return order

    def list_orders(
        self,
        current_user: User,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[OrderStatus] = None,
    ) -> list[Order]:
        if current_user.role == UserRole.ADMIN:
            return self.order_repo.list_orders(
                skip=skip,
                limit=limit,
                user_id=None,
                status=status_filter,
            )
        return self.order_repo.list_orders(
            skip=skip,
            limit=limit,
            user_id=current_user.id,
            status=status_filter,
        )

    def cancel_order_by_customer(self, order_id: int, user_id: int) -> Order:
        order = self.order_repo.get_by_id_and_user_id(order_id, user_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found.",
            )
        if order.status == OrderStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order is already cancelled.",
            )
        if order.status == OrderStatus.DELIVERED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel an order that has already been delivered.",
            )
        return self.order_repo.update_status(order, OrderStatus.CANCELLED)

    def update_order_status_by_admin(self, order_id: int, new_status: OrderStatus) -> Order:
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found.",
            )
        if order.status == new_status:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Order is already in {new_status.value} status.",
            )
        if order.status == OrderStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change status of a cancelled order.",
            )
        if order.status == OrderStatus.DELIVERED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change status of an already delivered order.",
            )

        if new_status == OrderStatus.DELIVERED:
            for item in order.items:
                product = self.product_repo.get_by_id(item.product_id, include_inactive=True)
                if not product or product.stock_quantity < item.quantity:
                    product_name = product.name if product else str(item.product_id)
                    available_stock = product.stock_quantity if product else 0
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Insufficient stock for product '{product_name}' (available: {available_stock}, required: {item.quantity}).",
                    )
            return self.order_repo.deliver_order(order)

        return self.order_repo.update_status(order, new_status)
