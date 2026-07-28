from sqlalchemy import Column, Integer, String, Float, Boolean
from src.database import Base
from pydantic import BaseModel, Field

#Pydantic model
class ProductSchema(BaseModel):
    id: int | None = None
    name: str
    unit: str
    cost_per_unit: float = Field(gt=0)
    price_per_unit: float = Field(gt=0)
    quantity_in_stock: float = Field(ge=0)


#SQLAlchemy model
class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    unit = Column(String)
    cost_per_unit = Column(Float)
    price_per_unit = Column(Float)
    quantity_in_stock = Column(Integer)
    is_active = Column(Boolean, default=True)