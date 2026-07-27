from fastapi import FastAPI, Response, status, Depends, HTTPException
from pydantic import BaseModel
from src.database import engine, Base, SessionLocal
from sqlalchemy.orm import Session
from src.models.product import Product, ProductSchema
from src.repositories.product_repository import ProductRepository

app = FastAPI()
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


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
    repository = ProductRepository(db)
    return repository.get_all_products()

@app.get("/products/search", response_model=ProductSchema)
def get_product(id: int | None = None, name: str | None = None, db: Session = Depends(get_db)):
    repository = ProductRepository(db)

    if id is not None:
        product = repository.get_product_by_id(id)
    elif name is not None:
        product = repository.get_product_by_name(name)
    else:
        raise HTTPException(status_code=400, detail="Must provide id or name")

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product
@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db:Session = Depends(get_db),
):
    repository = ProductRepository(db)
    product_was_deleted = repository.delete_product(product_id)

    if not product_was_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} was not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
