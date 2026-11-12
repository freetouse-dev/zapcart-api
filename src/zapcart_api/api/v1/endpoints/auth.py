from fastapi import APIRouter, Depends, status

from zapcart_api.api.deps import get_auth_service, get_current_user
from zapcart_api.models import User
from zapcart_api.schemas import (
    LoginRequest,
    MessageResponse,
    TokenResponse,
    UserRegister,
    UserResponse,
)
from zapcart_api.services import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new customer",
)
def register(
    user_in: UserRegister,
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    return auth_service.register(user_in)

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User login",
)
def login(
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    return auth_service.login(login_data)

@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="User logout",
)
def logout(
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    return MessageResponse(message="Successfully logged out.")

@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile (with role)",
)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user