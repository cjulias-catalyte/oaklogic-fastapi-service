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

