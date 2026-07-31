from fastapi import FastAPI, Response, status, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.database import engine, Base, SessionLocal
# 1. Import BOTH models so SQLAlchemy creates both tables
from src.models.product import Product, Category, ProductSchema, CategorySchema, CategoryCreate
from src.repositories.product_repository import ProductRepository, ProductUpdateRepository
from src.repositories.category_repository import CategoryRepository

app = FastAPI()

# Drop & create tables at startup (Day 3 pattern)
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
# CATEGORY ENDPOINTS (NEW)
# ==========================================

@app.post("/categories", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
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
# PRODUCT ENDPOINTS (UPDATED WITH FK CHECK)
# ==========================================

@app.post("/products", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
def create_product(product_data: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product.

    Validates that the referenced category exists before creating the product.

    Args:
        product_data: The product information.
        db: The active database session.

    Returns:
        The newly created product.

    Raises:
        HTTPException: If the category does not exist or the product already exists.
    """
    # 1. Validate that the referenced category exists BEFORE inserting
    if product_data.category_id is not None:
        cat_repo = CategoryRepository(db)
        category = cat_repo.get_category_by_id(product_data.category_id)

        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with ID {product_data.category_id} does not exist",
            )

    # 2. Proceed with product creation
    repository = ProductRepository(db)
    existing_product = repository.get_product_by_exact_name(product_data.name)

    if existing_product is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Product '{product_data.name}' already exists",
    )

    try:
        new_product = repository.create_new_product(product_data)
        db.expire_all()
        return new_product
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_CONFLICT,
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
    cleaned_name = product_name.strip()

    
    exact_product = repository.get_product_by_exact_name(cleaned_name)
    """Delete a product by its name.

    Args:
        product_name: The name of the product to delete.
        db: The active database session.

    Returns:
        A 204 No Content response.

    Raises:
        HTTPException: If the product does not exist.
    """

    if exact_product is not None:
        repository.delete_product_by_name(cleaned_name)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    # No exact match, so check whether the input partially matches products
    matches = repository.search_products_by_name(cleaned_name)

    if len(matches) > 1:
        matching_names = [product.name for product in matches]

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

@app.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Delete a category by its ID.

    Only allowed if the category has no products assigned to it.

    Args:
        category_id: The ID of the category to delete.
        db: The active database session.

    Returns:
        A 204 No Content response.

    Raises:
        HTTPException: If the category does not exist, or if it still has products.
    """
    repo = CategoryRepository(db)
    category = repo.get_category_by_id(category_id)

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} was not found",
        )

    if len(category.products) > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Category '{category.name}' has {len(category.products)} "
                "product(s) assigned to it and cannot be deleted."
            ),
        )

    repo.delete_category_by_id(category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)