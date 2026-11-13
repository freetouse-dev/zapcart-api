import uuid
from decimal import Decimal
import pytest
from fastapi.testclient import TestClient

from zapcart_api.core.enums import UserRole
from zapcart_api.core.security import create_access_token, hash_password
from zapcart_api.database.session import SessionLocal
from zapcart_api.main import app
from zapcart_api.models import Category, Product, User
from zapcart_api.repositories import CartRepository

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="function")
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def test_admin_user(db):
    email = f"admin_{uuid.uuid4().hex[:8]}@zapcart.com"
    user = User(
        username=f"admin_{uuid.uuid4().hex[:6]}",
        email=email,
        hashed_password=hash_password("adminpass123"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_customer_user(db):
    email = f"cust_{uuid.uuid4().hex[:8]}@zapcart.com"
    user = User(
        username=f"cust_{uuid.uuid4().hex[:6]}",
        email=email,
        hashed_password=hash_password("custpass123"),
        role=UserRole.CUSTOMER,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    cart_repo = CartRepository(db)
    cart_repo.create_cart(user.id)
    return user

@pytest.fixture(scope="function")
def admin_headers(test_admin_user):
    token = create_access_token(
        data={"sub": str(test_admin_user.id), "email": test_admin_user.email, "role": test_admin_user.role.value}
    )
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="function")
def customer_headers(test_customer_user):
    token = create_access_token(
        data={"sub": str(test_customer_user.id), "email": test_customer_user.email, "role": test_customer_user.role.value}
    )
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="function")
def test_category(db):
    uid = uuid.uuid4().hex[:6]
    category = Category(
        name=f"Category {uid}",
        slug=f"category-{uid}",
        is_active=True,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@pytest.fixture(scope="function")
def test_product(db, test_category):
    uid = uuid.uuid4().hex[:6]
    product = Product(
        category_id=test_category.id,
        name=f"Product {uid}",
        slug=f"product-{uid}",
        price=Decimal("49.99"),
        stock_quantity=50,
        is_active=True,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product
