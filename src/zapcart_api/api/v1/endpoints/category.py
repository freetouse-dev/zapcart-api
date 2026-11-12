from fastapi import APIRouter, Depends, Query, status

from zapcart_api.api.deps import (
    get_category_service,
    get_current_user,
    require_admin,
)
from zapcart_api.core.enums import UserRole
from zapcart_api.models import Category, User
from zapcart_api.schemas import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    MessageResponse,
)
from zapcart_api.services import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.get(
    "/",
    response_model=list[CategoryResponse],
    status_code=status.HTTP_200_OK,
    summary="List all categories",
)
def list_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    include_inactive: bool = Query(False),
    current_user: User = Depends(get_current_user),
    category_service: CategoryService = Depends(get_category_service),
) -> list[Category]:
    allow_inactive = include_inactive if current_user.role == UserRole.ADMIN else False
    return category_service.list_categories(
        skip=skip,
        limit=limit,
        include_inactive=allow_inactive,
    )

@router.get(
    "/slug/{slug}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get category by slug",
)
def get_category_by_slug(
    slug: str,
    current_user: User = Depends(get_current_user),
    category_service: CategoryService = Depends(get_category_service),
) -> Category:
    allow_inactive = True if current_user.role == UserRole.ADMIN else False
    return category_service.get_category_by_slug(
        slug=slug,
        include_inactive=allow_inactive,
    )

@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get category by ID",
)
def get_category_by_id(
    category_id: int,
    current_user: User = Depends(get_current_user),
    category_service: CategoryService = Depends(get_category_service),
) -> Category:
    allow_inactive = True if current_user.role == UserRole.ADMIN else False
    return category_service.get_category_by_id(
        category_id=category_id,
        include_inactive=allow_inactive,
    )

@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new category (Admin only)",
)
def create_category(
    category_in: CategoryCreate,
    admin_user: User = Depends(require_admin),
    category_service: CategoryService = Depends(get_category_service),
) -> Category:
    return category_service.create_category(category_in)

@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Update category (Admin only)",
)
def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    admin_user: User = Depends(require_admin),
    category_service: CategoryService = Depends(get_category_service),
) -> Category:
    return category_service.update_category(category_id, category_in)

@router.delete(
    "/{category_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Soft delete a category (Admin only)",
)
def delete_category(
    category_id: int,
    admin_user: User = Depends(require_admin),
    category_service: CategoryService = Depends(get_category_service),
) -> MessageResponse:
    category_service.delete_category(category_id)
    return MessageResponse(message="Category successfully deleted.")

@router.post(
    "/{category_id}/restore",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Restore a soft-deleted category (Admin only)",
)
def restore_category(
    category_id: int,
    admin_user: User = Depends(require_admin),
    category_service: CategoryService = Depends(get_category_service),
) -> Category:
    return category_service.restore_category(category_id)
