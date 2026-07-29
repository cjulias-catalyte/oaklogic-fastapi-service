import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.main import app, get_db
from src.database import Base

# ==========================================
# TEST DATABASE SETUP (IN-MEMORY SQLITE)
# ==========================================

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Overrides the FastAPI dependency to use an isolated test database."""
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


def test_search_products_by_name():
    # Setup product first since each test runs on a clean DB
    client.post(
        "/products",
        json={
            "name": "Basil Plant - 4in Pot",
            "unit": "each",
            "cost_per_unit": 1.75,
            "price_per_unit": 4.99,
            "quantity_in_stock": 40
        }
    )

    response = client.get("/products/filter/?name=Basil")

    assert response.status_code == 200

    products = response.json()

    assert len(products) > 0
    assert products[0]["name"] == "Basil Plant - 4in Pot"


# ==========================================
# NEW TESTS: GET & SEARCH METHODS
# ==========================================

def test_get_all_products():
    response = client.get("/products")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_product_by_id_success():
    create_res = client.post(
        "/products",
        json={
            "name": get_unique_name("Tomato"),
            "unit": "each",
            "cost_per_unit": 1.50,
            "price_per_unit": 3.99,
            "quantity_in_stock": 25
        }
    )
    product_id = create_res.json()["id"]

    response = client.get(f"/products/search/{product_id}")
    assert response.status_code == 200
    assert response.json()["id"] == product_id


def test_get_product_by_id_not_found():
    response = client.get("/products/search/999999")
    assert response.status_code == 404


def test_get_product_by_name_success():
    name = get_unique_name("Mint Plant")
    client.post(
        "/products",
        json={
            "name": name,
            "unit": "each",
            "cost_per_unit": 1.00,
            "price_per_unit": 2.99,
            "quantity_in_stock": 15
        }
    )

    response = client.get(f"/products/search/{name}")
    assert response.status_code == 200
    assert response.json()["name"] == name


def test_get_product_by_name_not_found():
    response = client.get("/products/search/NonExistentProduct")
    assert response.status_code == 404


def test_search_products_multi_params():
    client.post(
        "/products",
        json={
            "name": get_unique_name("Fern"),
            "unit": "each",
            "cost_per_unit": 1.75,
            "price_per_unit": 4.99,
            "quantity_in_stock": 10
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

def test_update_product_by_id():
    create_res = client.post(
        "/products",
        json={
            "name": "Old Plant Name",
            "unit": "each",
            "cost_per_unit": 2.00,
            "price_per_unit": 5.00,
            "quantity_in_stock": 10
        }
    )
    product_id = create_res.json()["id"]

    update_payload = {
        "id": product_id,
        "name": "Updated Plant Name",
        "unit": "each",
        "cost_per_unit": 2.50,
        "price_per_unit": 6.00,
        "quantity_in_stock": 12
    }

    response = client.put(f"/products/{product_id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Plant Name"
    assert response.json()["cost_per_unit"] == 2.50


def test_update_product_by_name():
    name = get_unique_name("Target Plant")
    client.post(
        "/products",
        json={
            "name": name,
            "unit": "each",
            "cost_per_unit": 2.00,
            "price_per_unit": 5.00,
            "quantity_in_stock": 10
        }
    )

    update_payload = {
        "name": "Updated Target Plant",
        "unit": "pack",
        "cost_per_unit": 3.00,
        "price_per_unit": 7.00,
        "quantity_in_stock": 20
    }

    response = client.put(f"/products/{name}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Target Plant"
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
    # Passing zero or negative ID triggers your custom 400 Bad Request
    response = client.put("/products/0", json=update_payload)
    assert response.status_code == 400


# ==========================================
# NEW TESTS: DELETE METHODS
# ==========================================

def test_delete_product_by_id():
    create_res = client.post(
        "/products",
        json={
            "name": get_unique_name("Plant To Delete"),
            "unit": "each",
            "cost_per_unit": 1.00,
            "price_per_unit": 2.00,
            "quantity_in_stock": 5
        }
    )
    product_id = create_res.json()["id"]

    delete_res = client.delete(f"/products/{product_id}")
    assert delete_res.status_code in [200, 204]

    # Verify it is actually gone
    get_res = client.get(f"/products/search/{product_id}")
    assert get_res.status_code == 404


def test_delete_product_by_id_not_found():
    response = client.delete("/products/999999")
    assert response.status_code == 404


def test_delete_product_by_name():
    name = get_unique_name("Named Plant To Delete")
    client.post(
        "/products",
        json={
            "name": name,
            "unit": "each",
            "cost_per_unit": 1.00,
            "price_per_unit": 2.00,
            "quantity_in_stock": 5
        }
    )

    delete_res = client.delete(f"/products/name/{name}")
    assert delete_res.status_code in [200, 204]

    # Verify deletion
    get_res = client.get(f"/products/search/{name}")
    assert get_res.status_code == 404


def test_delete_product_by_name_not_found():
    response = client.delete("/products/name/DoesNotExist12345")
    assert response.status_code == 404