from fastapi import Depends, FastAPI, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.database import Base, SessionLocal, engine
from src.models.product import (
    Category,
    CategoryCreate,
    CategorySchema,
    Product,
    ProductCreate,
    ProductSchema,
)
from src.repositories.category_repository import CategoryRepository
from src.repositories.product_repository import (
    ProductRepository,
    ProductUpdateRepository,
)

app = FastAPI()

# Drop & create tables on startup
Base.metadata.drop_all(bind=engine)
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


# ==========================================
# CATEGORY ENDPOINTS
# ==========================================


@app.post(
    "/categories",
    response_model=CategorySchema,
    status_code=status.HTTP_201_CREATED,
)
def create_category(category_data: CategoryCreate, db: Session = Depends(get_db)):
    repo = CategoryRepository(db)
    try:
        return repo.create_category(category_data)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Category '{category_data.name}' already exists",
        )


@app.get("/categories", response_model=list[CategorySchema])
def get_categories(db: Session = Depends(get_db)):
    repo = CategoryRepository(db)
    return repo.get_all_categories()


@app.get("/categories/{category_id}", response_model=CategorySchema)
def get_category_by_id(category_id: int, db: Session = Depends(get_db)):
    repo = CategoryRepository(db)
    category = repo.get_category_by_id(category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} was not found",
        )
    return category


# ==========================================
# PRODUCT ENDPOINTS
# ==========================================


@app.post(
    "/products",
    response_model=ProductSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    product_data: ProductCreate | ProductSchema, db: Session = Depends(get_db)
):
    # 1. Normalize category_id: convert <= 0 to None
    if product_data.category_id is not None and product_data.category_id <= 0:
        product_data.category_id = None

    # 2. Check if category exists before inserting
    if product_data.category_id is not None:
        cat_repo = CategoryRepository(db)
        category = cat_repo.get_category_by_id(product_data.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with ID {product_data.category_id} does not exist",
            )

    repository = ProductRepository(db)
    try:
        new_product = repository.create_new_product(product_data)
        db.expire_all()
        return new_product
    except IntegrityError as e:
        db.rollback()
        err_str = str(e.orig).lower() if hasattr(e, "orig") else ""
        if "foreign key" in err_str or "foreignkey" in err_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with ID {product_data.category_id} does not exist",
            )
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
    product_data: ProductCreate | ProductSchema,
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