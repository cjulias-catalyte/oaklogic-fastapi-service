from fastapi import FastAPI
from src.models.product import Product
from src.repositories.product_repository import ProductRepository

app = FastAPI()
products = ProductRepository()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello, {name}!"}

@app.post("/products",status_code=201)
def create_product(product: Product):
    products.add_product(product)
    return product

@app.get("/products")
async def get_products():
    return products.get_all()

@app.get("/products/search")
def search_products(name: str, unit: str = "each"):
    results = [p for p in products.get_all() if name.lower() in p.name.lower()]
    # Since unit defaults to "each", it will never be None.
    results = [p for p in results if p.unit.lower() == unit.lower()]
    return results