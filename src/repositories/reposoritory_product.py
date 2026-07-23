from src.models.product import Product

# Module-level list: persists across requests while the process is running,
# but is reinitialized to [] whenever the server restarts.
_products: list[Product] = []


def add_product(product: Product) -> Product:
    stored = product.model_copy()
    _products.append(stored)
    return stored


def get_all_products() -> list[Product]:
    return list(_products)


def _reset_store() -> None:
    _products.clear()
