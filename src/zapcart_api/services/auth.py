from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from zapcart_api.core.enums import UserRole
from zapcart_api.core.security import create_access_token, hash_password, verify_password
from zapcart_api.models import User
from zapcart_api.repositories import CartRepository, UserRepository
from zapcart_api.schemas import LoginRequest, TokenResponse, UserRegister

class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.cart_repo = CartRepository(db)

    def register(self, user_in: UserRegister) -> User:
        existing_user = self.user_repo.get_by_email(user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email is already registered.",
            )

        hashed_password = hash_password(user_in.password)
        new_user = self.user_repo.create(
            username=user_in.username,
            email=user_in.email,
            hashed_password=hashed_password,
            role=UserRole.CUSTOMER,
            is_active=True,
        )

        self.cart_repo.create_cart(user_id=new_user.id)
        return new_user

    def login(self, login_data: LoginRequest) -> TokenResponse:
        user = self.user_repo.get_by_email(login_data.email)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "role": user.role.value,
            }
        )
        return TokenResponse(access_token=access_token, token_type="bearer")