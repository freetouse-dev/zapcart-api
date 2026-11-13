def test_add_product_to_cart(client, customer_headers, test_product):
    payload = {
        "product_id": test_product.id,
        "quantity": 2,
    }
    response = client.post("/api/v1/cart/items", json=payload, headers=customer_headers)
    assert response.status_code == 200
    data = response.json()
    assert any(item["product_id"] == test_product.id for item in data["items"])

def test_view_customer_cart(client, customer_headers, test_product):
    client.post("/api/v1/cart/items", json={"product_id": test_product.id, "quantity": 1}, headers=customer_headers)
    response = client.get("/api/v1/cart/", headers=customer_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_price" in data
    assert "items" in data

def test_update_cart_item_quantity(client, customer_headers, test_product):
    client.post("/api/v1/cart/items", json={"product_id": test_product.id, "quantity": 1}, headers=customer_headers)
    response = client.put(f"/api/v1/cart/items/{test_product.id}", json={"quantity": 4}, headers=customer_headers)
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        if item["product_id"] == test_product.id:
            assert item["quantity"] == 4

def test_admin_cannot_access_cart(client, admin_headers):
    response = client.get("/api/v1/cart/", headers=admin_headers)
    assert response.status_code == 403

def test_clear_cart(client, customer_headers, test_product):
    client.post("/api/v1/cart/items", json={"product_id": test_product.id, "quantity": 1}, headers=customer_headers)
    response = client.delete("/api/v1/cart/items", headers=customer_headers)
    assert response.status_code == 200
    cart_res = client.get("/api/v1/cart/", headers=customer_headers)
    assert len(cart_res.json()["items"]) == 0
