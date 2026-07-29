from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


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


def test_get_products():
    # Setup: Create 'soil' product so the read assertions pass on an empty database
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
    assert response.json()[0]["name"] == "soil"
    assert response.json()[0]["unit"] == "bag"


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
    assert len(results) > 0
    assert results[0]["unit"] == "pot"


def test_filter_products_empty_results():
    response = client.get("/products/filter/?name=UnknownPlantFilter")
    assert response.status_code == 200
    assert response.json() == []