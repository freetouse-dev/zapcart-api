from decimal import Decimal
from typing import Any, Optional
from sqlalchemy.orm import Session, joinedload

from zapcart_api.core.enums import OrderStatus
from zapcart_api.models import Order, OrderItem, Product

class OrderRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, order_id: int) -> Optional[Order]:
        return (
            self.db.query(Order)
            .options(joinedload(Order.items).joinedload(OrderItem.product))
            .filter(Order.id == order_id)
            .first()
        )

    def get_by_id_and_user_id(self, order_id: int, user_id: int) -> Optional[Order]:
        return (
            self.db.query(Order)
            .options(joinedload(Order.items).joinedload(OrderItem.product))
            .filter(Order.id == order_id, Order.user_id == user_id)
            .first()
        )

    def list_orders(
        self,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None,
        status: Optional[OrderStatus] = None,
    ) -> list[Order]:
        query = (
            self.db.query(Order)
            .options(joinedload(Order.items).joinedload(OrderItem.product))
            .order_by(Order.created_at.desc())
        )
        if user_id is not None:
            query = query.filter(Order.user_id == user_id)
        if status is not None:
            query = query.filter(Order.status == status)
        return query.offset(skip).limit(limit).all()

    def create_order(
        self,
        user_id: int,
        total_price: Decimal,
        items_data: list[dict[str, Any]],
    ) -> Order:
        order = Order(
            user_id=user_id,
            total_price=total_price,
            status=OrderStatus.PENDING,
        )
        self.db.add(order)
        self.db.flush()

        for item_data in items_data:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data["product_id"],
                quantity=item_data["quantity"],
                price_at_purchase=item_data["price_at_purchase"],
            )
            self.db.add(order_item)

        self.db.commit()
        return self.get_by_id(order.id)

    def update_status(self, order: Order, new_status: OrderStatus) -> Order:
        order.status = new_status
        self.db.commit()
        self.db.refresh(order)
        return order

    def deliver_order(self, order: Order) -> Order:
        for item in order.items:
            product = self.db.query(Product).filter(Product.id == item.product_id).with_for_update().first()
            if product:
                product.stock_quantity = max(0, product.stock_quantity - item.quantity)
        order.status = OrderStatus.DELIVERED
        self.db.commit()
        self.db.refresh(order)
        return order
