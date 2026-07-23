from fastapi import FastAPI

from src.models.product import Product


class ProductRepository:
    def __init__(self):
        self._products: list[Product] = []

    def add_product(self, product: Product) -> None:
        self._products.append(product)

    def get_all(self) -> list[Product]:
        return self._products


