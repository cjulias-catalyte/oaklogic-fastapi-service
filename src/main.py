from fastapi import FastAPI, Response, status, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.database import engine, Base, SessionLocal
# 1. IMPORTANT: Import Product BEFORE calling create_all() so the table registers
from src.models.product import Product, ProductSchema
from src.repositories.product_repository import ProductRepository, ProductUpdateRepository

app = FastAPI()

# 2. Now SQLAlchemy knows about the Product table when this runs
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
def say_hello(name: str):
    return {"message": f"Hello, {name}!"}


@app.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    count = db.query(Product).count()
    return {"product_count": count}


@app.post("/products", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
def create_product(product_data: ProductSchema, db: Session = Depends(get_db)):
    repository = ProductRepository(db)
    try:
        return repository.create_new_product(product_data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Product '{product_data.name}' already exists",
        )


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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product '{identifier}' was not found",
        )

    return product


@app.get("/products/filter/", response_model=list[ProductSchema])
def filter_products(
    name: str | None = None,
    unit: str | None = None,
    cost_per_unit: float | None = None,
    price_per_unit: float | None = None,
    quantity_in_stock: float | None = None,
    db: Session = Depends(get_db),
):
    repository = ProductRepository(db)
    return repository.search_products(
        name=name,
        unit=unit,
        cost_per_unit=cost_per_unit,
        price_per_unit=price_per_unit,
        quantity_in_stock=quantity_in_stock,
    )


@app.delete("/products/{product_id}")
def delete_product_by_id(product_id: int, db: Session = Depends(get_db)):
    repository = ProductRepository(db)
    if not repository.delete_product_by_id(product_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} was not found",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.delete("/products/name/{product_name}")
def delete_product_by_name(product_name: str, db: Session = Depends(get_db)):
    repository = ProductRepository(db)
    if not repository.delete_product_by_name(product_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with name '{product_name}' was not found",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/products/{identifier}", response_model=ProductSchema)
def update_product(
    identifier: str,
    product_data: ProductSchema,
    db: Session = Depends(get_db),
):
    repository = ProductUpdateRepository()

    if identifier.isdigit():
        product_id = int(identifier)
        if product_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product ID must be greater than 0.",
            )
        product = repository.update_product(
            db=db,
            product_data=product_data,
            product_id=product_id,
        )
    else:
        product = repository.update_product(
            db=db,
            product_data=product_data,
            product_name=identifier,
        )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return product