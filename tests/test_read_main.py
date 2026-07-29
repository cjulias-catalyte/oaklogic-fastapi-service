import pytest
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
    assert response.json()["product_count"] == 0  # Clean DB starts at 0


def test_get_products():
    # Setup: Create 'soil' product
    client.post(
        "/products",
        json={
            "name": "soil",
            "unit": "bag",
            "cost_per_unit": 3.5,
            "price_per_unit": 5.5,
            "quantity_in_stock": 10
        }
    )
    
    response = client.get("/products")
    assert response.status_code == 200
    products = response.json()
    assert len(products) == 1
    assert products[0]["name"] == "soil"
    assert products[0]["unit"] == "bag"


# ==========================================
# SINGLE PRODUCT RETRIEVAL (READ) TESTS
# ==========================================

def test_get_product_by_id_success():
    create_res = client.post(
        "/products",
        json={
            "name": "Tomato Plant",
            "unit": "each",
            "cost_per_unit": 2.00,
            "price_per_unit": 5.00,
            "quantity_in_stock": 15
        }
    )
    product_id = create_res.json()["id"]

    response = client.get(f"/products/search/{product_id}")
    assert response.status_code == 200
    assert response.json()["id"] == product_id
    assert response.json()["name"] == "Tomato Plant"


def test_get_product_by_id_not_found():
    response = client.get("/products/search/999999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_product_by_name_success():
    client.post(
        "/products",
        json={
            "name": "Mint Plant",
            "unit": "each",
            "cost_per_unit": 1.50,
            "price_per_unit": 3.99,
            "quantity_in_stock": 20
        }
    )

    response = client.get("/products/search/Mint Plant")
    assert response.status_code == 200
    assert response.json()["name"] == "Mint Plant"


def test_get_product_by_name_not_found():
    response = client.get("/products/search/NonExistentPlant123")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# ==========================================
# FILTERING PRODUCTS (READ) TESTS
# ==========================================

def test_filter_products_by_params():
    client.post(
        "/products",
        json={
            "name": "Rose Bush",
            "unit": "pot",
            "cost_per_unit": 10.00,
            "price_per_unit": 25.00,
            "quantity_in_stock": 5
        }
    )

    response = client.get("/products/filter/?unit=pot&cost_per_unit=10.0")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["name"] == "Rose Bush"
    assert results[0]["unit"] == "pot"


def test_filter_products_empty_results():
    response = client.get("/products/filter/?name=UnknownPlantFilter")
    assert response.status_code == 200
    assert response.json() == []