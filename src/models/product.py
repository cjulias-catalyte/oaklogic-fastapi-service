from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Float
from src.database import Base


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
    
    __tablename__ = 'product'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    unit= Column(String, index=True)
    cost_per_unit = Column(Float, index=True)
    price_per_unit = Column(Float, index=True) 
    quantity_in_stock = Column(Float, index=True)