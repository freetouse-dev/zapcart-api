from fastapi import APIRouter

from zapcart_api.api.v1.endpoints import (
    auth_router,
    cart_router,
    category_router,
    health_router,
    order_router,
    product_router,
)

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(category_router)
api_router.include_router(product_router)
api_router.include_router(cart_router)
api_router.include_router(order_router)

__all__ = ["api_router"]