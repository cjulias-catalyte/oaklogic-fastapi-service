from src.models.product import Product, ProductCreate

# Module-level list: persists across requests while the process is running,
# but is reinitialized to [] whenever the server restarts.
_products: list[Product] = []
_next_id: int = 1


def add_product(product: ProductCreate) -> Product:
    global _next_id
    stored = Product(id=_next_id, **product.model_dump())
    _products.append(stored)
    _next_id += 1
    return stored


def get_all_products() -> list[Product]:
    return list(_products)
