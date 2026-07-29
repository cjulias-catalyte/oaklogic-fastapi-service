from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


# ==========================================
# EXISTING TESTS (Kept as-is + setup fix)
# ==========================================

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
    

def test_say_hello():
    response = client.get("/hello/Bob")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Bob!"}


def test_get_products():
    # Setup: Create 'soil' product so the existing assertions pass on an empty database
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
# NEW TESTS: HEALTH CHECK & CREATE
# ==========================================

def test_db_check():
    response = client.get("/db-check")
    assert response.status_code == 200
    assert "product_count" in response.json()
    assert isinstance(response.json()["product_count"], int)


def test_create_product_success():
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
    data = response.json()
    assert data["name"] == "Basil Plant - 4in Pot"
    assert data["cost_per_unit"] == 1.75
    assert "id" in data


def test_create_product_invalid_data():
    # Missing required fields should return 422 Unprocessable Entity
    response = client.post(
        "/products",
        json={"name": "Incomplete Product"}
    )
    assert response.status_code == 422


# ==========================================
# NEW TESTS: SINGLE PRODUCT RETRIEVAL
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
# NEW TESTS: FILTERING PRODUCTS
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


# ==========================================
# NEW TESTS: UPDATE PRODUCT
# ==========================================

def test_update_product_by_id_success():
    create_res = client.post(
        "/products",
        json={
            "name": "Old Lavender",
            "unit": "each",
            "cost_per_unit": 2.00,
            "price_per_unit": 6.00,
            "quantity_in_stock": 10
        }
    )
    product_id = create_res.json()["id"]

    update_payload = {
        "id": product_id,
        "name": "Updated Lavender",
        "unit": "each",
        "cost_per_unit": 2.50,
        "price_per_unit": 7.00,
        "quantity_in_stock": 15
    }

    response = client.put(f"/products/{product_id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Lavender"
    assert response.json()["price_per_unit"] == 7.00


def test_update_product_by_name_success():
    client.post(
        "/products",
        json={
            "name": "Fern Plant",
            "unit": "each",
            "cost_per_unit": 3.00,
            "price_per_unit": 8.00,
            "quantity_in_stock": 12
        }
    )

    update_payload = {
        "name": "Fern Plant",
        "unit": "hanging basket",
        "cost_per_unit": 4.00,
        "price_per_unit": 10.00,
        "quantity_in_stock": 8
    }

    response = client.put("/products/Fern Plant", json=update_payload)
    assert response.status_code == 200
    assert response.json()["unit"] == "hanging basket"


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
    assert response.json()["detail"] == "Product not found"


def test_update_product_invalid_id_zero():
    update_payload = {
        "name": "Invalid ID Plant",
        "unit": "each",
        "cost_per_unit": 1.00,
        "price_per_unit": 2.00,
        "quantity_in_stock": 5
    }
    response = client.put("/products/0", json=update_payload)
    assert response.status_code == 400
    assert "greater than 0" in response.json()["detail"]


# ==========================================
# NEW TESTS: DELETE PRODUCT
# ==========================================

def test_delete_product_by_id_success():
    create_res = client.post(
        "/products",
        json={
            "name": "Cactus",
            "unit": "each",
            "cost_per_unit": 1.00,
            "price_per_unit": 3.00,
            "quantity_in_stock": 5
        }
    )
    product_id = create_res.json()["id"]

    delete_res = client.delete(f"/products/{product_id}")
    assert delete_res.status_code == 204

    # Confirm it was removed
    get_res = client.get(f"/products/search/{product_id}")
    assert get_res.status_code == 404


def test_delete_product_by_id_not_found():
    response = client.delete("/products/999999")
    assert response.status_code == 404
    assert "was not found" in response.json()["detail"]


def test_delete_product_by_name_success():
    client.post(
        "/products",
        json={
            "name": "Orchid",
            "unit": "pot",
            "cost_per_unit": 5.00,
            "price_per_unit": 15.00,
            "quantity_in_stock": 3
        }
    )

    delete_res = client.delete("/products/name/Orchid")
    assert delete_res.status_code == 204

    # Confirm it was removed
    get_res = client.get("/products/search/Orchid")
    assert get_res.status_code == 404


def test_delete_product_by_name_not_found():
    response = client.delete("/products/name/NonExistentPlantToDel")
    assert response.status_code == 404
    assert "was not found" in response.json()["detail"]