from sqlalchemy import Column, Integer, String, Float, Boolean
from src.database import Base

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    unit = Column(String)
    cost_per_unit = Column(Float)
    price_per_unit = Column(Float)
    quantity_in_stock = Column(Integer)
    is_active = Column(Boolean, default=True)