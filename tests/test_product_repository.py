from fastapi.testclient import TestClient
from src.repositories.product_repository import app

client = TestClient(app)

def test_create_product():
    response = client.post(
        "/products",
        json={
            "name": "Basil Plant - 4in Pot",
            "unit": "each",
            "cost_per_unit": 1.75,
            "price_per_unit": 4.99,
            "quantity_in_stock": 40
        }
    )

    assert response.status_code == 201

    assert response.json()["name"] == "Basil Plant - 4in Pot"

def test_create_product_invalid_price_type():
    response = client.post(
        "/products",
        json={
            "name": "Fertilizer",
            "unit": "bag",
            "cost_per_unit": "not a number",
            "price_per_unit": 20.00,
            "quantity_in_stock": 10
        }
    )

    assert response.status_code == 422

def test_create_product_missing_quantity():
    response = client.post(
        "/products",
        json={
            "name": "Rose Plant",
            "unit": "each",
            "cost_per_unit": 5.00,
            "price_per_unit": 12.99
        }
    )

    assert response.status_code == 422

def test_create_product_no_data():
    response = client.post("/products")

    assert response.status_code == 422