from fastapi import FastAPI, Query
from src.models.product import Product

app = FastAPI()

products = []

@app.post("/products", status_code=201)
def create_product(product: Product):
    products.append(product)
    return product 

@app.get("/products/search")
def search_products(
    name: str,
    unit: str = Query(default=None)
):
    results = []

    for product in products:
        if name.lower() in product.name.lower():
            if unit is None or product.unit.lower() == unit.lower():
                results.append(product)

    return results