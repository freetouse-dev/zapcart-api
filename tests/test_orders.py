def test_buy_now(client, customer_headers, test_product):
    payload = {
        "product_id": test_product.id,
        "quantity": 2,
    }
    response = client.post("/api/v1/orders/buy-now", json=payload, headers=customer_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"
    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == test_product.id
    assert data["items"][0]["quantity"] == 2

def test_checkout_cart(client, customer_headers, test_product):
    client.post("/api/v1/cart/items", json={"product_id": test_product.id, "quantity": 1}, headers=customer_headers)
    response = client.post("/api/v1/orders/checkout-cart", headers=customer_headers)
    assert response.status_code == 201
    cart_res = client.get("/api/v1/cart/", headers=customer_headers)
    assert len(cart_res.json()["items"]) == 0

def test_checkout_single_cart_item(client, customer_headers, test_product):
    client.post("/api/v1/cart/items", json={"product_id": test_product.id, "quantity": 1}, headers=customer_headers)
    response = client.post(f"/api/v1/orders/checkout-cart/{test_product.id}", headers=customer_headers)
    assert response.status_code == 201
    cart_res = client.get("/api/v1/cart/", headers=customer_headers)
    assert not any(item["product_id"] == test_product.id for item in cart_res.json()["items"])

def test_cancel_order_by_customer(client, customer_headers, test_product):
    order_res = client.post(
        "/api/v1/orders/buy-now",
        json={"product_id": test_product.id, "quantity": 1},
        headers=customer_headers,
    )
    order_id = order_res.json()["id"]
    response = client.post(f"/api/v1/orders/{order_id}/cancel", headers=customer_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"

def test_admin_update_order_status_delivered(client, customer_headers, admin_headers, test_product):
    stock_before = test_product.stock_quantity
    order_res = client.post(
        "/api/v1/orders/buy-now",
        json={"product_id": test_product.id, "quantity": 2},
        headers=customer_headers,
    )
    order_id = order_res.json()["id"]
    response = client.patch(
        f"/api/v1/orders/{order_id}/status",
        json={"status": "delivered"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "delivered"
    prod_res = client.get(f"/api/v1/products/{test_product.id}", headers=customer_headers)
    assert prod_res.json()["stock_quantity"] == stock_before - 2

def test_order_role_authorization(client, customer_headers, admin_headers, test_product):
    admin_buy = client.post(
        "/api/v1/orders/buy-now",
        json={"product_id": test_product.id, "quantity": 1},
        headers=admin_headers,
    )
    assert admin_buy.status_code == 403
    cust_order = client.post(
        "/api/v1/orders/buy-now",
        json={"product_id": test_product.id, "quantity": 1},
        headers=customer_headers,
    )
    order_id = cust_order.json()["id"]
    cust_status_update = client.patch(
        f"/api/v1/orders/{order_id}/status",
        json={"status": "delivered"},
        headers=customer_headers,
    )
    assert cust_status_update.status_code == 403
