from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from src.database import engine, Base, SessionLocal
from sqlalchemy.orm import Session
from src.models.product import Product, ProductSchema
from src.repositories import delete_repository
from src.repositories.product_repository import ProductRepository



app = FastAPI()
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

products = ProductRepository()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    deleted_product = delete_repository.delete_product(
        db,
        product_id,
    )

    if deleted_product is None:
        raise HTTPException(
            status_code=404,
            detail=f"Product with ID {product_id} was not found",
        )

    return {
        "message": "Product deleted successfully",
        "product_id": product_id,
    }
