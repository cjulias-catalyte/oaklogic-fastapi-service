from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from src.database import engine, Base, SessionLocal
from sqlalchemy.orm import Session
from src.models.product import Product, ProductSchema
from src.repositories.product_repository import ProductRepository

app = FastAPI()
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

<<<<<<< HEAD
products = ProductRepository()
=======
>>>>>>> 21fff00e22c1342205d96eb2324b8922131fda5f

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello, {name}!"}

# @app.post("/products", status_code=201)
# def create_product(product: ProductSchema):
#     products.add_product(product)
#     return product

# @app.get("/products")
# async def get_products():
#     return products.get_all()

# @app.get("/products/search")
# def search_products(name: str, unit: str = "each"):
#     results = [p for p in products.get_all() if name.lower() in p.name.lower()]

#     if unit is not None:
#         results = [p for p in results if p.unit.lower() == unit.lower()]

#     return results


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    count = db.query(Product).count()
    return {"product_count": count}

@app.post("/products", response_model=ProductSchema, status_code=201)
def create_product(product_data: ProductSchema, db: Session = Depends(get_db)):
    repository = ProductRepository(db)
    return repository.create_new_product(product_data)


@app.get("/products", response_model=list[ProductSchema])
def get_products(db: Session = Depends(get_db)):
<<<<<<< HEAD
    return db.query(Product).all()


def search_products(db: Session, name: str):
    # Returns all matches or empty list
    return db.query(Product).filter(Product.name.ilike(f"%{name}%")).all()

def get_product(db: Session, product_id: int):
    # Returns the item or None
    return db.query(Product).filter(Product.id == product_id).first()
=======
    repository = ProductRepository(db)
    return repository.get_all_products()
>>>>>>> 21fff00e22c1342205d96eb2324b8922131fda5f
