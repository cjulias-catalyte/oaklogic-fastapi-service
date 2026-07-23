from fastapi import FastAPI
from src.models.product import Product

app = FastAPI()

products = []

@app.post("/products", status_code=201)
def create_product(product: Product):
    products.append(product)
    return product 