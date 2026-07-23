from fastapi import FastAPI

from src.models.product import Product
from src.repositories.product_repository import ProductRepository

app = FastAPI()

product_repository = ProductRepository()
product_repository.add_product(
    Product(
        name="soil",
        unit="bag",
        cost_per_unit=3.5,
        price_per_unit=5.5,
        quantity_in_stock=10,
    )
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello, {name}!"}


@app.get("/products")
async def get_products():
    return product_repository.get_all()