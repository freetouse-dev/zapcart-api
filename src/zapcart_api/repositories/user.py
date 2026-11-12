from typing import Any, Optional
from sqlalchemy.orm import Session

from zapcart_api.core.enums import UserRole
from zapcart_api.models import User

class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: int, include_inactive: bool = False) -> Optional[User]:
        query = self.db.query(User).filter(User.id == user_id)
        if not include_inactive:
            query = query.filter(User.is_active == True)
        return query.first()

    def get_by_email(self, email: str, include_inactive: bool = False) -> Optional[User]:
        query = self.db.query(User).filter(User.email == email)
        if not include_inactive:
            query = query.filter(User.is_active == True)
        return query.first()

    def get_by_username(self, username: str, include_inactive: bool = False) -> Optional[User]:
        query = self.db.query(User).filter(User.username == username)
        if not include_inactive:
            query = query.filter(User.is_active == True)
        return query.first()

    def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        include_inactive: bool = False,
    ) -> list[User]:
        query = self.db.query(User)
        if not include_inactive:
            query = query.filter(User.is_active == True)
        return query.offset(skip).limit(limit).all()

    def create(
        self,
        username: str,
        email: str,
        hashed_password: str,
        role: UserRole = UserRole.CUSTOMER,
        is_active: bool = True,
    ) -> User:
        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            role=role,
            is_active=is_active,
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def update(self, user: User, update_data: dict[str, Any]) -> User:
        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def soft_delete(self, user: User) -> User:
        user.soft_delete()
        self.db.commit()
        self.db.refresh(user)
        return user

    def restore(self, user: User) -> User:
        user.restore()
        self.db.commit()
        self.db.refresh(user)
        return user
