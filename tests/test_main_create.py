# tests/test_main_create.py
from fastapi.testclient import TestClient
from src.main import app
import pytest
import uuid

client = TestClient(app)

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

def test_create_product_happy_path(sample_category):
    """POST with valid data should create a product and return 201."""
    response = client.post("/products", json={
        "name": "Rosemary Plant",
        "unit": "each",
        "cost_per_unit": 2.50,
        "price_per_unit": 5.00,
        "quantity_in_stock": 15,
        "category_id": sample_category["id"]
    })

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Rosemary Plant"
    assert data["id"] is not None


def test_create_product_validation_failure():
    """POST with an invalid field (negative cost) should fail validation with 422."""
    response = client.post("/products", json={
        "name": "Flower",
        "unit": "each",
        "cost_per_unit": -5,  
        "price_per_unit": 10,
        "quantity_in_stock": 5
    })

    assert response.status_code == 422


def test_get_product_not_found():
    response = client.get("/products/search/doesnotexist")

    assert response.status_code == 404
    assert "was not found" in response.json()["detail"].lower()