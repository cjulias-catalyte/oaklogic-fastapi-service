import pytest

from src.models.product import Product
from src.repositories.reposoritory_product import add_product, get_all_products, _reset_store


@pytest.fixture(autouse=True)
def reset_store():
    _reset_store()
    yield
    _reset_store()


def test_create_product():
    product = Product(
        name="soil",
        unit="bag",
        cost_per_unit=3.5,
        price_per_unit=5.5,
        quantity_in_stock=10,
    )
    stored = add_product(product)

    assert stored.name == "soil"
    assert stored.unit == "bag"
    assert stored.cost_per_unit == 3.5
    assert stored.price_per_unit == 5.5
    assert stored.quantity_in_stock == 10


def test_products_persist_across_requests():
    product = Product(
        name="soil",
        unit="bag",
        cost_per_unit=3.5,
        price_per_unit=5.5,
        quantity_in_stock=10,
    )
    add_product(product)

    products = get_all_products()
    assert any(
        p.name == "soil"
        and p.unit == "bag"
        and p.cost_per_unit == 3.5
        and p.price_per_unit == 5.5
        and p.quantity_in_stock == 10
        for p in products
    )
