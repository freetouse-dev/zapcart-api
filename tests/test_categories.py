import uuid

def test_admin_create_category(client, admin_headers):
    uid = uuid.uuid4().hex[:6]
    payload = {
        "name": f"Cat_{uid}",
        "slug": f"cat-{uid}",
    }
    response = client.post("/api/v1/categories/", json=payload, headers=admin_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["slug"] == payload["slug"]

def test_customer_cannot_create_category(client, customer_headers):
    uid = uuid.uuid4().hex[:6]
    payload = {
        "name": f"Cat_{uid}",
        "slug": f"cat-{uid}",
    }
    response = client.post("/api/v1/categories/", json=payload, headers=customer_headers)
    assert response.status_code == 403

def test_list_categories(client, customer_headers, test_category):
    response = client.get("/api/v1/categories/", headers=customer_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

def test_get_category_by_id(client, customer_headers, test_category):
    response = client.get(f"/api/v1/categories/{test_category.id}", headers=customer_headers)
    assert response.status_code == 200
    assert response.json()["id"] == test_category.id

def test_admin_soft_delete_category(client, admin_headers, test_category):
    response = client.delete(f"/api/v1/categories/{test_category.id}", headers=admin_headers)
    assert response.status_code == 200
    assert "deleted" in response.json()["message"].lower()
