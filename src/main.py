from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from src.database import engine, Base, SessionLocal
from sqlalchemy.orm import Session
from src.models.product import Product, ProductSchema
from src.repositories.product_repository import ProductRepository
from src.repositories.Update_Product_Repository import ProductUpdateRepository
app = FastAPI()
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

products = ProductRepository()
update_repository = ProductUpdateRepository()


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


@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

@app.patch("/products/update", response_model=ProductSchema)
def update_product(
    product_data: ProductSchema,
    product_id: int | None = None,
    product_name: str | None = None,
    db: Session = Depends(get_db)
):
    product = update_repository.update_product(
        db=db,
        product_data=product_data,
        product_id=product_id,
        product_name=product_name
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product