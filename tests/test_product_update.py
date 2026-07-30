from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_update_existing_product():

    # Create product first
    create_response = client.post(
        "/products",
        json={
            "name": "Rose Bush",
            "unit": "each",
            "cost_per_unit": 10.00,
            "price_per_unit": 19.99,
            "quantity_in_stock": 20
        }
    )

    assert create_response.status_code == 201

    product_id = create_response.json()

    # Update product
    response = client.put(
        f"/products/{product_id['id']}",
        json={
            "id" : product_id ["id"],
            "name": "Rose Bush",
            "unit": "each",
            "cost_per_unit": 10.00,
            "price_per_unit": 24.99,
            "quantity_in_stock": 40
        }
    )

    assert response.status_code == 200

    updated = response.json()

    assert updated["name"] == "Rose Bush"
    assert updated["price_per_unit"] == 24.99
    assert updated["quantity_in_stock"] == 40