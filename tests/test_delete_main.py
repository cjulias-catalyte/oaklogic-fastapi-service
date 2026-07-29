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
    assert create_res.status_code == 201

    product_id = create_res.json()["id"]

    #Act
    delete_res = client.delete(f"/products/{product_id}")

    #Assert
    assert delete_res.status_code == 204

    get_res = client.get(f"/products/search/{product_id}")
    assert get_res.status_code == 404


def test_delete_product_by_id_not_found():

    #Act
    response = client.delete("/products/999999")

    #Assert
    assert response.status_code == 404
    assert "was not found" in response.json()["detail"]


def test_delete_product_by_name_success():
    create_res = client.post(
        "/products",
        json={
            "name": "Orchid",
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

    # Confirm it was removed
    get_res = client.get(f"/products/search/{product_name}")
    assert get_res.status_code == 404


def test_delete_product_by_name_not_found():

    #Act
    response = client.delete("/products/name/NonExistentPlantToDel")


    #Assert
    assert response.status_code == 404
    assert "was not found" in response.json()["detail"]