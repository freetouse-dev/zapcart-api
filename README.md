# ZapCart API

ZapCart API is a high-performance e-commerce backend built with FastAPI, PostgreSQL, and Redis. It provides role-based authentication, catalog management, shopping cart operations, order processing, rate limiting, and token revocation.

## Tech Stack

- **Framework**: FastAPI (Python 3.13+)
- **Database**: PostgreSQL with SQLAlchemy 2.0 and Alembic migrations
- **Cache & Rate Limiting**: Redis with SlowAPI
- **Authentication**: JWT (JSON Web Tokens) with Argon2 password hashing
- **Package Manager**: uv
- **Testing**: pytest

## Prerequisites

- Python >= 3.13
- uv package manager
- PostgreSQL running locally or remotely
- Redis running locally or remotely

## Setup & Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd zapcart-api
```

2. Install dependencies:
```bash
uv sync
```

3. Configure environment variables:
```bash
cp .env.example .env
```
Update `.env` with your PostgreSQL database credentials, Redis URL, and JWT secret key:
```ini
APP_NAME=Zapcart Platform
APP_VERSION=1.0.0
APP_ENVIRONMENT=development

DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=zapcart_db

REDIS_URL=redis://localhost:6379/0

JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRE_TIME=30
```

4. Run database migrations:
```bash
uv run alembic upgrade head
```

## Running the Application

Start the local development server:
```bash
uv run fastapi dev src/zapcart_api/main.py
```

The API will be available at:
- **Base URL**: `http://localhost:8000`
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Running Tests

Execute the automated test suite with pytest:
```bash
uv run pytest
```

To run a specific test file:
```bash
uv run pytest tests/test_orders.py
```

## Core Modules & Endpoints

### Health
- `GET /health` - Application health status
- `GET /health/db` - Database connection verification

### Authentication (`/api/v1/auth`)
- `POST /register` - Create customer or admin account
- `POST /login` - Authenticate and obtain JWT access token (rate-limited)
- `GET /me` - Get current authenticated user details
- `POST /logout` - Revoke JWT token via Redis blocklist

### Categories (`/api/v1/categories`)
- `GET /` - List all active categories
- `GET /{id}` - Get category details
- `POST /` - Create category (Admin only)
- `PUT /{id}` - Update category (Admin only)
- `DELETE /{id}` - Soft-delete category (Admin only)

### Products (`/api/v1/products`)
- `GET /` - List products with category/status filters
- `GET /{id}` - Get product by ID
- `GET /slug/{slug}` - Get product by URL slug
- `POST /` - Create product (Admin only)
- `PUT /{id}` - Update product (Admin only)
- `DELETE /{id}` - Soft-delete product (Admin only)

### Cart (`/api/v1/cart`) - Customer Only
- `GET /` - View current customer cart and calculated totals
- `POST /items` - Add product or increment quantity
- `PUT /items/{product_id}` - Update item quantity
- `DELETE /items/{product_id}` - Remove single item from cart
- `DELETE /items` - Clear entire cart

### Orders (`/api/v1/orders`)
- `POST /buy-now` - Direct single product purchase without cart (Customer)
- `POST /checkout-cart` - Checkout entire cart into order (Customer)
- `POST /checkout-cart/{product_id}` - Checkout specific item from cart (Customer)
- `GET /` - List orders (Customer views own; Admin views all)
- `GET /{id}` - Get order details with line items
- `POST /{id}/cancel` - Cancel pending order (Customer)
- `PATCH /{id}/status` - Update status; automatically decrements product stock upon delivery (Admin)
