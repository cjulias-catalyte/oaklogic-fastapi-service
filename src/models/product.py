from sqlalchemy import Column, Integer, String, Float
from src.database import Base

class Product(Base):
    
    __tablename__ = 'product'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    unit= Column(String, index=True)
    cost_per_unit = Column(Float, index=True)
    price_per_unit = Column(Float, index=True) 
    quantity_in_stock = Column(Float, index=True)