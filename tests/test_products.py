from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_create_product():
    response = client.post("/products", json={"name": "Widget", "price": 9.99})
    assert response.status_code == 201
    assert response.json() == {"id": 1, "name": "Widget", "price": 9.99}


def test_products_persist_across_requests():
    client.post("/products", json={"name": "Gadget", "price": 14.50})

    response = client.get("/products")
    assert response.status_code == 200
    products = response.json()
    assert any(p["name"] == "Gadget" and p["price"] == 14.50 for p in products)
