from fastapi.testclient import TestClient
from src.main import app
from uuid import uuid4

client = TestClient(app)


def test_delete_product_by_id_success():
    create_res = client.post(
        "/products",
        json={
            "name": f"Cactus{uuid4()}",
            "unit": "each",
            "cost_per_unit": 1.00,
            "price_per_unit": 3.00,
            "quantity_in_stock": 5,
        },
    )
    assert create_res.status_code == 201
    product_id = create_res.json()["id"]

    delete_res = client.delete(f"/products/{product_id}")
    assert delete_res.status_code == 204


def test_delete_product_by_id_not_found():
    response = client.delete("/products/999999")
    assert response.status_code == 404


def test_delete_product_by_name_success():
    create_res = client.post(
        "/products",
        json={
            "name":f"Orchid{uuid4()}",
            "unit": "pot",
            "cost_per_unit": 5.00,
            "price_per_unit": 15.00,
            "quantity_in_stock": 3
            }
    )
    assert create_res.status_code == 201
    product_name = create_res.json()["name"]

    delete_res = client.delete(f"/products/name/{product_name}")
    assert delete_res.status_code == 204


def test_delete_product_by_name_not_found():
    response = client.delete("/products/name/NonExistentPlantToDel")
    assert response.status_code == 404