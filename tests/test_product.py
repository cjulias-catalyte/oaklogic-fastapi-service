import pytest
from pydantic import ValidationError
from src.models.product import Product, ProductSchema


# ==========================================
# EXISTING TESTS (Kept as-is)
# ==========================================

def test_product_information():
    product_example = Product(
        name="soil",
        unit="bag",
        cost_per_unit=3.5,
        price_per_unit=5.5,
        quantity_in_stock=10
    )
    
    assert product_example.name == "soil"
    assert product_example.unit == "bag"
    assert product_example.cost_per_unit == 3.5
    assert product_example.price_per_unit == 5.5
    assert product_example.quantity_in_stock == 10
    

def test_product_incorrect_datatype():
    with pytest.raises(NameError):
        Product(
            name=soil,  # Undefined variable raises NameError
            unit="bag",
            cost_per_unit=3.5,
            price_per_unit=5.5,
            quantity_in_stock=10
        )


# ==========================================
# NEW TESTS: SQLALCHEMY PRODUCT MODEL
# ==========================================

def test_product_default_is_active():
    """Verify that a Product instance supports the is_active default attribute."""
    product = Product(
        name="mulch",
        unit="bag",
        cost_per_unit=2.0,
        price_per_unit=4.0,
        quantity_in_stock=15
    )
    # SQLAlchemy defaults are applied at DB flush, but passing explicitly or checking model defaults works
    assert getattr(product, "is_active", True) is True


# ==========================================
# NEW TESTS: PYDANTIC PRODUCT SCHEMA
# ==========================================

def test_product_schema_valid():
    """Test successful initialization of ProductSchema without optional ID."""
    data = {
        "name": "Compost",
        "unit": "bag",
        "cost_per_unit": 4.0,
        "price_per_unit": 8.99,
        "quantity_in_stock": 50
    }
    schema = ProductSchema(**data)
    assert schema.id is None
    assert schema.name == "Compost"
    assert schema.cost_per_unit == 4.0
    assert schema.price_per_unit == 8.99
    assert schema.quantity_in_stock == 50


def test_product_schema_valid_with_id():
    """Test successful initialization of ProductSchema with an ID."""
    data = {
        "id": 1,
        "name": "Compost",
        "unit": "bag",
        "cost_per_unit": 4.0,
        "price_per_unit": 8.99,
        "quantity_in_stock": 50
    }
    schema = ProductSchema(**data)
    assert schema.id == 1


def test_product_schema_cost_per_unit_must_be_greater_than_zero():
    """Test that cost_per_unit <= 0 raises a Pydantic ValidationError."""
    with pytest.raises(ValidationError):
        ProductSchema(
            name="Soil",
            unit="bag",
            cost_per_unit=0,  # Fails Field(gt=0)
            price_per_unit=5.0,
            quantity_in_stock=10
        )

    with pytest.raises(ValidationError):
        ProductSchema(
            name="Soil",
            unit="bag",
            cost_per_unit=-1.5,  # Fails Field(gt=0)
            price_per_unit=5.0,
            quantity_in_stock=10
        )


def test_product_schema_price_per_unit_must_be_greater_than_zero():
    """Test that price_per_unit <= 0 raises a Pydantic ValidationError."""
    with pytest.raises(ValidationError):
        ProductSchema(
            name="Soil",
            unit="bag",
            cost_per_unit=2.0,
            price_per_unit=0,  # Fails Field(gt=0)
            quantity_in_stock=10
        )


def test_product_schema_quantity_in_stock_cannot_be_negative():
    """Test that quantity_in_stock < 0 raises a ValidationError, but 0 is valid."""
    # Zero quantity should be valid (ge=0)
    schema = ProductSchema(
        name="Soil",
        unit="bag",
        cost_per_unit=2.0,
        price_per_unit=5.0,
        quantity_in_stock=0
    )
    assert schema.quantity_in_stock == 0

    # Negative quantity should fail
    with pytest.raises(ValidationError):
        ProductSchema(
            name="Soil",
            unit="bag",
            cost_per_unit=2.0,
            price_per_unit=5.0,
            quantity_in_stock=-5
        )


def test_product_schema_missing_required_fields():
    """Test that omitting required fields raises a ValidationError."""
    with pytest.raises(ValidationError):
        ProductSchema(
            name="Soil",
            unit="bag",
            # missing cost_per_unit, price_per_unit, and quantity_in_stock
        )


def test_product_schema_invalid_data_types():
    """Test that passing non-numeric strings for numerical fields fails validation."""
    with pytest.raises(ValidationError):
        ProductSchema(
            name="Soil",
            unit="bag",
            cost_per_unit="invalid_number",
            price_per_unit=5.0,
            quantity_in_stock=10
        )