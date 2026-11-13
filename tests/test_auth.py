import uuid

def test_register_customer(client):
    uid = uuid.uuid4().hex[:6]
    payload = {
        "username": f"user_{uid}",
        "email": f"user_{uid}@example.com",
        "password": "strongpassword123",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["role"] == "customer"

def test_login_success(client, test_customer_user):
    payload = {
        "email": test_customer_user.email,
        "password": "custpass123",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_password(client, test_customer_user):
    payload = {
        "email": test_customer_user.email,
        "password": "wrongpassword",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401

def test_get_current_user_profile(client, customer_headers, test_customer_user):
    response = client.get("/api/v1/auth/me", headers=customer_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_customer_user.email

def test_logout_and_token_revocation(client, customer_headers):
    res_logout = client.post("/api/v1/auth/logout", headers=customer_headers)
    assert res_logout.status_code == 200

    res_me = client.get("/api/v1/auth/me", headers=customer_headers)
    assert res_me.status_code == 401
