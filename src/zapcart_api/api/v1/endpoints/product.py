from typing import Optional
from fastapi import APIRouter, Depends, Query, status

from zapcart_api.api.deps import (
    get_current_user,
    get_product_service,
    require_admin,
)
from zapcart_api.core.enums import UserRole
from zapcart_api.models import Product, User
from zapcart_api.schemas import (
    MessageResponse,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)
from zapcart_api.services import ProductService

router = APIRouter(prefix="/products", tags=["Products"])

@router.get(
    "/",
    response_model=list[ProductResponse],
    status_code=status.HTTP_200_OK,
    summary="List all products",
)
def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category_id: Optional[int] = Query(None),
    include_inactive: bool = Query(False),
    current_user: User = Depends(get_current_user),
    product_service: ProductService = Depends(get_product_service),
) -> list[Product]:
    allow_inactive = include_inactive if current_user.role == UserRole.ADMIN else False
    return product_service.list_products(
        skip=skip,
        limit=limit,
        category_id=category_id,
        include_inactive=allow_inactive,
    )

@router.get(
    "/slug/{slug}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Get product by slug",
)
def get_product_by_slug(
    slug: str,
    current_user: User = Depends(get_current_user),
    product_service: ProductService = Depends(get_product_service),
) -> Product:
    allow_inactive = True if current_user.role == UserRole.ADMIN else False
    return product_service.get_product_by_slug(
        slug=slug,
        include_inactive=allow_inactive,
    )

@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Get product by ID",
)
def get_product_by_id(
    product_id: int,
    current_user: User = Depends(get_current_user),
    product_service: ProductService = Depends(get_product_service),
) -> Product:
    allow_inactive = True if current_user.role == UserRole.ADMIN else False
    return product_service.get_product_by_id(
        product_id=product_id,
        include_inactive=allow_inactive,
    )

@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product (Admin only)",
)
def create_product(
    product_in: ProductCreate,
    admin_user: User = Depends(require_admin),
    product_service: ProductService = Depends(get_product_service),
) -> Product:
    return product_service.create_product(product_in)

@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Update product (Admin only)",
)
def update_product(
    product_id: int,
    product_in: ProductUpdate,
    admin_user: User = Depends(require_admin),
    product_service: ProductService = Depends(get_product_service),
) -> Product:
    return product_service.update_product(product_id, product_in)

@router.delete(
    "/{product_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Soft delete a product (Admin only)",
)
def delete_product(
    product_id: int,
    admin_user: User = Depends(require_admin),
    product_service: ProductService = Depends(get_product_service),
) -> MessageResponse:
    product_service.delete_product(product_id)
    return MessageResponse(message="Product successfully deleted.")

@router.post(
    "/{product_id}/restore",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Restore a soft-deleted product (Admin only)",
)
def restore_product(
    product_id: int,
    admin_user: User = Depends(require_admin),
    product_service: ProductService = Depends(get_product_service),
) -> Product:
    return product_service.restore_product(product_id)
