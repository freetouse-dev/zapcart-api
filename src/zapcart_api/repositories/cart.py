from typing import Optional
from sqlalchemy.orm import Session, joinedload

from zapcart_api.models import Cart, CartItem

class CartRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_user_id(self, user_id: int) -> Optional[Cart]:
        return (
            self.db.query(Cart)
            .options(joinedload(Cart.items).joinedload(CartItem.product))
            .filter(Cart.user_id == user_id)
            .first()
        )

    def create_cart(self, user_id: int) -> Cart:
        cart = Cart(user_id=user_id)
        self.db.add(cart)
        self.db.commit()
        self.db.refresh(cart)
        return cart

    def get_or_create_cart(self, user_id: int) -> Cart:
        cart = self.get_by_user_id(user_id)
        if not cart:
            cart = self.create_cart(user_id)
        return cart

    def get_cart_item(self, cart_id: int, product_id: int) -> Optional[CartItem]:
        return (
            self.db.query(CartItem)
            .options(joinedload(CartItem.product))
            .filter(CartItem.cart_id == cart_id, CartItem.product_id == product_id)
            .first()
        )

    def add_or_update_item(self, cart_id: int, product_id: int, quantity: int = 1) -> CartItem:
        item = self.get_cart_item(cart_id, product_id)
        if item:
            item.quantity += quantity
        else:
            item = CartItem(cart_id=cart_id, product_id=product_id, quantity=quantity)
            self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update_item_quantity(self, cart_id: int, product_id: int, quantity: int) -> Optional[CartItem]:
        item = self.get_cart_item(cart_id, product_id)
        if item:
            item.quantity = quantity
            self.db.commit()
            self.db.refresh(item)
        return item

    def remove_item(self, cart_id: int, product_id: int) -> bool:
        item = self.get_cart_item(cart_id, product_id)
        if item:
            self.db.delete(item)
            self.db.commit()
            return True
        return False

    def clear_cart(self, cart_id: int) -> None:
        self.db.query(CartItem).filter(CartItem.cart_id == cart_id).delete()
        self.db.commit()
