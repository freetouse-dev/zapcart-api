import uuid

def test_admin_create_product(client, admin_headers, test_category):
    uid = uuid.uuid4().hex[:6]
    payload = {
        "category_id": test_category.id,
        "name": f"Prod_{uid}",
        "slug": f"prod-{uid}",
        "price": 29.99,
        "stock_quantity": 25,
    }
    response = client.post("/api/v1/products/", json=payload, headers=admin_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["category_id"] == test_category.id

def test_customer_cannot_create_product(client, customer_headers, test_category):
    uid = uuid.uuid4().hex[:6]
    payload = {
        "category_id": test_category.id,
        "name": f"Prod_{uid}",
        "slug": f"prod-{uid}",
        "price": 29.99,
        "stock_quantity": 25,
    }
    response = client.post("/api/v1/products/", json=payload, headers=customer_headers)
    assert response.status_code == 403

def test_list_products(client, customer_headers, test_product):
    response = client.get("/api/v1/products/", headers=customer_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(p["id"] == test_product.id for p in data)

def test_get_product_by_id(client, customer_headers, test_product):
    response = client.get(f"/api/v1/products/{test_product.id}", headers=customer_headers)
    assert response.status_code == 200
    assert response.json()["id"] == test_product.id

def test_get_product_by_slug(client, customer_headers, test_product):
    response = client.get(f"/api/v1/products/slug/{test_product.slug}", headers=customer_headers)
    assert response.status_code == 200
    assert response.json()["slug"] == test_product.slug
