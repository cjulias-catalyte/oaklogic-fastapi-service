from fastapi.testclient import TestClient
from src.main import app
import uuid
from uuid import uuid4
import pytest

client = TestClient(app)


<<<<<<< HEAD
# ==========================================
# NEW TESTS: DELETE PRODUCT
# ==========================================

def get_unique_name(base_name: str) -> str:
    """Generates a unique string by appending a short UUID to the base name."""
    return f"{base_name}_{uuid.uuid4().hex[:8]}"

@pytest.fixture
def sample_category():
    unique_name = get_unique_name("General")

    response = client.post(
        "/categories",
        json={"name": unique_name},
    )

    assert response.status_code == 201

    return response.json()

def test_delete_product_by_id_success(sample_category):
=======
def test_delete_product_by_id_success():
>>>>>>> 53e57553e08b2fe6d45f4300a40425aeee259435
    create_res = client.post(
        "/products",
        json={
            "name": f"Cactus{uuid4()}",
            "unit": "each",
            "cost_per_unit": 1.00,
            "price_per_unit": 3.00,
            "quantity_in_stock": 5,
<<<<<<< HEAD
            "category_id": sample_category["id"]
        }
=======
        },
>>>>>>> 53e57553e08b2fe6d45f4300a40425aeee259435
    )
    assert create_res.status_code == 201
    product_id = create_res.json()["id"]

    delete_res = client.delete(f"/products/{product_id}")
    assert delete_res.status_code == 204


def test_delete_product_by_id_not_found():
    response = client.delete("/products/999999")
    assert response.status_code == 404


def test_delete_product_by_name_success(sample_category):
    create_res = client.post(
        "/products",
        json={
            "name": f"Orchid{uuid4()}",
            "unit": "pot",
            "cost_per_unit": 5.00,
            "price_per_unit": 15.00,
            "quantity_in_stock": 3,
            "category_id": sample_category["id"]
        }
    )
    assert create_res.status_code == 201
    product_name = create_res.json()["name"]
<<<<<<< HEAD

    delete_res = client.delete(f"/products/name/{product_name}")
    assert delete_res.status_code == 204
=======
>>>>>>> 53e57553e08b2fe6d45f4300a40425aeee259435

    delete_res = client.delete(f"/products/name/{product_name}")
    assert delete_res.status_code == 204


def test_delete_product_by_name_not_found():
    response = client.delete("/products/name/NonExistentPlantToDel")
<<<<<<< HEAD

    assert response.status_code == 404
    assert "NonExistentPlantToDel" in response.json()["detail"]
=======
    assert response.status_code == 404
>>>>>>> 53e57553e08b2fe6d45f4300a40425aeee259435
