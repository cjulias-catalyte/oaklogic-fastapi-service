import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

# 1. Import Product first so it registers with Base.metadata immediately
from src.models.product import Product
# 2. Use the shared engine from src.database
from src.database import Base, engine
from src.main import app, get_db

# ==========================================
# TEST DATABASE SETUP (SHARED IN-MEMORY)
# ==========================================

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def get_unique_name(prefix: str = "item") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


# ==========================================
# BASIC GET / READ TESTS
# ==========================================


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_say_hello():
    response = client.get("/hello/Bob")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Bob!"}


def test_db_check():
    response = client.get("/db-check")
    assert response.status_code == 200
    assert "product_count" in response.json()
    assert isinstance(response.json()["product_count"], int)
    assert response.json()["product_count"] == 0


def test_get_products():
    unique_name = get_unique_name("soil")
    client.post(
        "/products",
        json={
            "name": unique_name,
            "unit": "bag",
            "cost_per_unit": 3.5,
            "price_per_unit": 5.5,
            "quantity_in_stock": 10,
        },
    )

    response = client.get("/products")
    assert response.status_code == 200
    names = [p["name"] for p in response.json()]
    assert unique_name in names


# ==========================================
# SINGLE PRODUCT RETRIEVAL (READ) TESTS
# ==========================================


def test_get_product_by_id_success():
    unique_name = get_unique_name("Tomato")
    create_res = client.post(
        "/products",
        json={
            "name": unique_name,
            "unit": "each",
            "cost_per_unit": 2.00,
            "price_per_unit": 5.00,
            "quantity_in_stock": 15,
        },
    )
    product_id = create_res.json()["id"]

    response = client.get(f"/products/search/{product_id}")
    assert response.status_code == 200
    assert response.json()["id"] == product_id
    assert response.json()["name"] == unique_name


def test_get_product_by_id_not_found():
    response = client.get("/products/search/999999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_product_by_name_success():
    unique_name = get_unique_name("Mint")
    client.post(
        "/products",
        json={
            "name": unique_name,
            "unit": "each",
            "cost_per_unit": 1.50,
            "price_per_unit": 3.99,
            "quantity_in_stock": 20,
        },
    )

    response = client.get(f"/products/search/{unique_name}")
    assert response.status_code == 200
    assert response.json()["name"] == unique_name


def test_get_product_by_name_not_found():
    response = client.get("/products/search/NonExistentPlant123")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# ==========================================
# FILTERING PRODUCTS (READ) TESTS
# ==========================================


def test_filter_products_by_params():
    unique_name = get_unique_name("Rose")
    client.post(
        "/products",
        json={
            "name": unique_name,
            "unit": "pot",
            "cost_per_unit": 10.00,
            "price_per_unit": 25.00,
            "quantity_in_stock": 5,
        },
    )

    response = client.get("/products/filter/?unit=pot&cost_per_unit=10.0")
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    assert any(p["name"] == unique_name for p in results)


def test_filter_products_empty_results():
    response = client.get("/products/filter/?name=UnknownPlantFilter")
    assert response.status_code == 200
    assert response.json() == []