from zapcart_api.api.v1.endpoints.auth import router as auth_router
from zapcart_api.api.v1.endpoints.cart import router as cart_router
from zapcart_api.api.v1.endpoints.category import router as category_router
from zapcart_api.api.v1.endpoints.health import router as health_router
from zapcart_api.api.v1.endpoints.order import router as order_router
from zapcart_api.api.v1.endpoints.product import router as product_router

__all__ = [
    "auth_router",
    "cart_router",
    "category_router",
    "health_router",
    "order_router",
    "product_router",
]
