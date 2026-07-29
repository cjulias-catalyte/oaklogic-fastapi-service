from fastapi.testclient import TestClient
from src.repositories.product_repository import app

client = TestClient(app)

# ==========================================
# EXISTING TESTS (Kept as-is)1
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
    response = client.get("/products/search?name=Basil")

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
    # Create a product first to ensure it exists
    create_res = client.post(
        "/products",
        json={
            "name": "Tomato Plant",
            "unit": "each",
            "cost_per_unit": 1.50,
            "price_per_unit": 3.99,
            "quantity_in_stock": 25
        }
    )
    product_id = create_res.json()["id"]

    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["id"] == product_id

def test_get_product_by_id_not_found():
    response = client.get("/products/999999")
    assert response.status_code == 404

def test_get_product_by_name_success():
    client.post(
        "/products",
        json={
            "name": "Mint Plant",
            "unit": "each",
            "cost_per_unit": 1.00,
            "price_per_unit": 2.99,
            "quantity_in_stock": 15
        }
    )

    response = client.get("/products/by-name?name=Mint Plant")
    assert response.status_code == 200
    assert "Mint" in response.json()["name"]

def test_get_product_by_name_not_found():
    response = client.get("/products/by-name?name=NonExistentProduct")
    assert response.status_code == 404

def test_search_products_multi_params():
    response = client.get("/products/search?unit=each&cost_per_unit=1.75")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_search_products_empty_results():
    response = client.get("/products/search?name=XYZNotRealPlant123")
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
    client.post(
        "/products",
        json={
            "name": "Target Plant Name",
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

    response = client.put("/products/by-name?name=Target Plant Name", json=update_payload)
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

def test_update_product_both_id_and_name_error():
    update_payload = {
        "name": "Conflict Plant",
        "unit": "each",
        "cost_per_unit": 1.00,
        "price_per_unit": 2.00,
        "quantity_in_stock": 5
    }
    # Testing endpoint that incorrectly supplies both identifier parameters
    response = client.put("/products/update?product_id=1&product_name=Conflict Plant", json=update_payload)
    assert response.status_code in [400, 422]


# ==========================================
# NEW TESTS: DELETE METHODS
# ==========================================

def test_delete_product_by_id():
    create_res = client.post(
        "/products",
        json={
            "name": "Plant To Delete",
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
    get_res = client.get(f"/products/{product_id}")
    assert get_res.status_code == 404

def test_delete_product_by_id_not_found():
    response = client.delete("/products/999999")
    assert response.status_code == 404

def test_delete_product_by_name():
    client.post(
        "/products",
        json={
            "name": "Named Plant To Delete",
            "unit": "each",
            "cost_per_unit": 1.00,
            "price_per_unit": 2.00,
            "quantity_in_stock": 5
        }
    )

    delete_res = client.delete("/products/by-name?name=Named Plant To Delete")
    assert delete_res.status_code in [200, 204]

    # Verify deletion
    get_res = client.get("/products/by-name?name=Named Plant To Delete")
    assert get_res.status_code == 404

def test_delete_product_by_name_not_found():
    response = client.delete("/products/by-name?name=DoesNotExist12345")
    assert response.status_code == 404