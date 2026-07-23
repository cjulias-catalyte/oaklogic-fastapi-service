from pydantic import BaseModel
from decimal import Decimal

class Product(BaseModel):
    name: str
    unit: str
    cost_per_unit: Decimal
    price_per_unit: Decimal
    quantity_in_stock: float