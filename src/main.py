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

@app.get("/products/search/{identifier}", response_model=ProductSchema)
def get_product(identifier: str, db: Session = Depends(get_db)):
    repository = ProductRepository(db)

    if identifier.isdigit():
        product = repository.get_product_by_id(int(identifier))
    else:
        product = repository.get_product_by_name(identifier)

    if product is None:
        if identifier.isdigit():
            raise HTTPException(status_code=404, detail=f"Product with Id: {identifier} was not found")
        else:
            raise HTTPException(status_code=404, detail=f"Product with name '{identifier}' was not found")
    
    return product

@app.get("/products/filter/", response_model=list[ProductSchema])
def get_products(name: str | None = None, unit: str | None = None, cost_per_unit: float | None = None, price_per_unit: float | None = None, quantity_in_stock: float | None = None,
    db: Session = Depends(get_db)):
    
    repository = ProductRepository(db)
    return repository.search_products(name=name, unit=unit, cost_per_unit=cost_per_unit, price_per_unit=price_per_unit, quantity_in_stock=quantity_in_stock,)
    
    
@app.delete("/products/{product_id}")
def delete_product_by_id(
    product_id: int,
    db:Session = Depends(get_db),
):
    repository = ProductRepository(db)

    product_was_deleted = repository.delete_product_by_id(product_id)


    if not product_was_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} was not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.delete("/products/name/{product_name}")
def delete_product_by_name(
    product_name: str,
    db:Session = Depends(get_db),
):
    repository = ProductRepository(db)

    product_was_deleted = repository.delete_product_by_name(product_name)


    if not product_was_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_name} was not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
