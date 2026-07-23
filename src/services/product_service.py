from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str
    unit: str
    # Cost per unit must be greater than 0, as business costs cannot be negative or zero.
    cost_per_unit: float = Field(gt=0)
    # Price per unit is usually positive as well, you might consider gt=0 here too.
    price_per_unit: float = Field(gt=0)
    # Quantity in stock can be 0 (out of stock), but not negative.
    quantity_in_stock: float = Field(ge=0)