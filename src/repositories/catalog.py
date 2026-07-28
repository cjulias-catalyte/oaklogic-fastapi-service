
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from src.database import engine, Base, SessionLocal
from sqlalchemy.orm import Session
from src.models.product import Product, ProductSchema
from src.repositories.product_repository import ProductRepository

app = FastAPI()

# Note: Keeping the drop/create logic as per Day 3 requirements
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

products = ProductRepository()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. Create a product
@app.post("/products", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
def create_product(product_data: ProductSchema, db: Session = Depends(get_db)):
    db_product = Product(
        id=product_data.id,
        name=product_data.name,
        unit=product_data.unit,
        cost_per_unit=product_data.cost_per_unit,
        price_per_unit=product_data.price_per_unit,
        quantity_in_stock=product_data.quantity_in_stock,
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# 2. Get all products (supports optional ?id=... filter)
@app.get("/products", response_model=list[ProductSchema])
def get_products(id: int = None, db: Session = Depends(get_db)):
    # If an ID is provided, filter by it
    if id:
        product = db.query(Product).filter(Product.id == id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Product with ID {id} not found"
            )
        return [product] # Return as a list to match response_model
    
    # Otherwise, return all products
    return db.query(Product).all()

# 3. Search products by name (using a query parameter)
@app.get("/products/search", response_model=list[ProductSchema])
def search_products(name: str, db: Session = Depends(get_db)):
    # Query for products where the name matches the provided string
    products = db.query(Product).filter(Product.name.ilike(f"%{name}%")).all()
    
    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No products found with name containing '{name}'"
        )
    return products

# 4. Get ONE product by ID (using the path parameter)
@app.get("/products/{product_id}", response_model=ProductSchema)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    # Query for the specific item
    product = db.query(Product).filter(Product.id == product_id).first()
        
    # Requirement 4: Handle the case where the product is not found
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )
    return product

@app.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    count = db.query(Product).count()
    return {"product_count": count}