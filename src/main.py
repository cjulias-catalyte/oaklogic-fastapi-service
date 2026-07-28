from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel, Field
from src.database import engine, Base, SessionLocal
from sqlalchemy.orm import Session
from src.repositories.product_repository import ProductRepository

# Define Schema here to ensure validation (Field constraints)
class ProductSchema(BaseModel):
    id: int
    name: str
    unit: str
    cost_per_unit: float = Field(gt=0, description="Cost must be greater than 0")
    price_per_unit: float = Field(gt=0, description="Price must be greater than 0")
    quantity_in_stock: int = Field(ge=0, description="Quantity cannot be negative")

    class Config:
        from_attributes = True

app = FastAPI()

# Database Setup
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- DIAGNOSTICS ---
@app.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    return {"product_count": len(repo.get_all_products())}

# --- ROUTES ---

@app.post("/products", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
def create_product(product_data: ProductSchema, db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    return repo.create_new_product(product_data)

@app.get("/products", response_model=list[ProductSchema])
def get_products(db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    return repo.get_all_products()

@app.get("/products/search", response_model=list[ProductSchema])
def search_products(name: str, db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    products = repo.get_products_by_name(name)
    if not products:
        raise HTTPException(status_code=404, detail=f"No products found with name containing '{name}'")
    return products

@app.get("/products/{product_id}", response_model=ProductSchema)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    product = repo.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
    return product

@app.put("/products/{product_id}", response_model=ProductSchema)
def update_product(product_id: int, product_data: ProductSchema, db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    updated_product = repo.update_product(product_id, product_data)
    if not updated_product:
        raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
    return updated_product

# --- DELETE ROUTES (SPECIFIC MUST COME BEFORE GENERIC) ---

@app.delete("/products/by-name/{name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_by_name(name: str, db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    success = repo.delete_products_by_name(name)
    if not success:
        raise HTTPException(status_code=404, detail=f"No products found with name '{name}'")
    return None

@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    success = repo.delete_product(product_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
    return None