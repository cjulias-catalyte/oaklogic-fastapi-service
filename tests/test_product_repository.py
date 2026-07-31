import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

# 1. Import Product first to ensure model registration
from src.models.product import Product
# 2. Use the SHARED engine from src.database instead of creating a new one
from src.database import Base, engine
from src.main import app, get_db

# ==========================================
# TEST DATABASE SETUP (SHARED IN-MEMORY)
# ==========================================

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Overrides the FastAPI dependency to use the isolated test session."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    """Create fresh tables before each test and drop them afterward."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def get_unique_name(prefix: str = "Plant") -> str:
    """Helper to avoid naming collisions when running tests."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


# ==========================================
# EXISTING TESTS (Kept as-is, routes aligned)
# ==========================================

@pytest.fixture
def sample_category():
    response = client.post("/categories", json={"name": "General"})
    return response.json()

def test_create_product(sample_category):
    unique_name = get_unique_name("Basil Plant - 4in Pot")
    response = client.post(
        "/products",
        json={
            "name": unique_name,
            "unit": "each",
            "cost_per_unit": 1.75,
            "price_per_unit": 4.99,
            "quantity_in_stock": 40,
            "category_id": sample_category["id"]
        }
    )

    assert response.status_code == 201
    assert response.json()["name"] == unique_name


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


def test_search_products_by_name(sample_category,):
    unique_name = get_unique_name("Basil Plant - Search Pot")
    client.post(
        "/products",
        json={
            "name": unique_name,
            "unit": "each",
            "cost_per_unit": 1.75,
            "price_per_unit": 4.99,
            "quantity_in_stock": 40,
            "category_id": sample_category["id"]
        }
    )

    response = client.get(f"/products/filter/?name={unique_name}")

    assert response.status_code == 200

    products = response.json()

    assert len(products) > 0
    assert products[0]["name"] == unique_name


# ==========================================
# NEW TESTS: GET & SEARCH METHODS
# ==========================================

def test_get_all_products():
    response = client.get("/products")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_product_by_id_success(sample_category,):
    create_res = client.post(
        "/products",
        json={
            "name": get_unique_name("Tomato"),
            "unit": "each",
            "cost_per_unit": 1.50,
            "price_per_unit": 3.99,
            "quantity_in_stock": 25,
            "category_id": sample_category["id"]
        }
    )
    product_id = create_res.json()["id"]

    response = client.get(f"/products/search/{product_id}")
    assert response.status_code == 200
    assert response.json()["id"] == product_id


def test_get_product_by_id_not_found():
    response = client.get("/products/search/999999")
    assert response.status_code == 404


def test_get_product_by_name_success(sample_category,):
    name = get_unique_name("Mint Plant")
    client.post(
        "/products",
        json={
            "name": name,
            "unit": "each",
            "cost_per_unit": 1.00,
            "price_per_unit": 2.99,
            "quantity_in_stock": 15,
            "category_id": sample_category["id"]
        }
    )

    response = client.get(f"/products/search/{name}")
    assert response.status_code == 200
    assert response.json()["name"] == name


def test_get_product_by_name_not_found():
    response = client.get("/products/search/NonExistentProduct")
    assert response.status_code == 404


def test_search_products_multi_params(sample_category,):
    client.post(
        "/products",
        json={
            "name": get_unique_name("Fern"),
            "unit": "each",
            "cost_per_unit": 1.75,
            "price_per_unit": 4.99,
            "quantity_in_stock": 10,
            "category_id": sample_category["id"]
        }
    )
    response = client.get("/products/filter/?unit=each&cost_per_unit=1.75")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0


def test_search_products_empty_results():
    response = client.get("/products/filter/?name=XYZNotRealPlant123")
    assert response.status_code == 200
    assert response.json() == []


# ==========================================
# NEW TESTS: UPDATE METHODS
# ==========================================

def test_update_product_by_id(sample_category,):
    create_res = client.post(
        "/products",
        json={
            "name": get_unique_name("Old Plant Name"),
            "unit": "each",
            "cost_per_unit": 2.00,
            "price_per_unit": 5.00,
            "quantity_in_stock": 10,
            "category_id": sample_category["id"]
        }
    )
    product_id = create_res.json()["id"]

    updated_name = get_unique_name("Updated Plant Name")
    update_payload = {
        "id": product_id,
        "name": updated_name,
        "unit": "each",
        "cost_per_unit": 2.50,
        "price_per_unit": 6.00,
        "quantity_in_stock": 12
    }

    response = client.put(f"/products/{product_id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["name"] == updated_name
    assert response.json()["cost_per_unit"] == 2.50


def test_update_product_by_name(sample_category,):
    name = get_unique_name("Target Plant")
    client.post(
        "/products",
        json={
            "name": name,
            "unit": "each",
            "cost_per_unit": 2.00,
            "price_per_unit": 5.00,
            "quantity_in_stock": 10,
            "category_id": sample_category["id"]
        }
    )

    updated_name = get_unique_name("Updated Target Plant")
    update_payload = {
        "name": updated_name,
        "unit": "pack",
        "cost_per_unit": 3.00,
        "price_per_unit": 7.00,
        "quantity_in_stock": 20
    }

    response = client.put(f"/products/{name}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["name"] == updated_name
    assert response.json()["unit"] == "pack"


def test_update_product_not_found():
    update_payload = {
        "name": "Ghost Plant",
        "unit": "each",
        "cost_per_unit": 1.00,
        "price_per_unit": 2.00,
        "quantity_in_stock": 5
    }
    response = client.put("/products/999999", json=update_payload)
    assert response.status_code == 404


def test_update_product_invalid_id():
    update_payload = {
        "name": "Conflict Plant",
        "unit": "each",
        "cost_per_unit": 1.00,
        "price_per_unit": 2.00,
        "quantity_in_stock": 5
    }
    response = client.put("/products/0", json=update_payload)
    assert response.status_code == 400


# ==========================================
# NEW TESTS: DELETE METHODS
# ==========================================

def test_delete_product_by_id(sample_category,):
    create_res = client.post(
        "/products",
        json={
            "name": get_unique_name("Plant To Delete"),
            "unit": "each",
            "cost_per_unit": 1.00,
            "price_per_unit": 2.00,
            "quantity_in_stock": 5,
            "category_id": sample_category["id"]
        }
    )
    product_id = create_res.json()["id"]

    delete_res = client.delete(f"/products/{product_id}")
    assert delete_res.status_code in [200, 204]

    get_res = client.get(f"/products/search/{product_id}")
    assert get_res.status_code == 404


def test_delete_product_by_id_not_found():
    response = client.delete("/products/999999")
    assert response.status_code == 404


def test_delete_product_by_name(sample_category,):
    name = get_unique_name("Named Plant To Delete")
    client.post(
        "/products",
        json={
            "name": name,
            "unit": "each",
            "cost_per_unit": 1.00,
            "price_per_unit": 2.00,
            "quantity_in_stock": 5,
            "category_id": sample_category["id"]
        }
    )

    delete_res = client.delete(f"/products/name/{name}")
    assert delete_res.status_code in [200, 204]

    get_res = client.get(f"/products/search/{name}")
    assert get_res.status_code == 404


def test_delete_product_by_name_not_found():
    response = client.delete("/products/name/DoesNotExist12345")
    assert response.status_code == 404