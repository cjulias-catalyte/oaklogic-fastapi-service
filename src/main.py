from fastapi import FastAPI

from src.models.product import Product
from src.repositories.product_repository import product_repository

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello, {name}!"}


@app.post("/products")
def create_product(product: Product):
    product_repository.add_product(product)
    return product


@app.get("/products")
async def get_products():
    return product_repository.get_all()