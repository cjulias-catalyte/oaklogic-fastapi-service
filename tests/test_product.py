import pytest
from src.models.product import Product 

def test_product_information():
    product_example = Product(name="soil", unit="bag", cost_per_unit=3.5, price_per_unit=5.5, quantity_in_stock=10)
    
    assert product_example.name == "soil"
    assert product_example.unit == "bag"
    assert product_example.cost_per_unit == 3.5
    assert product_example.price_per_unit == 5.5
    assert product_example.quantity_in_stock == 10
    
def test_product_incorrect_datatype():
    with pytest.raises(NameError):
        Product(name=soil, unit="bag", cost_per_unit=3.5, price_per_unit=5.5, quantity_in_stock=10)
        

        