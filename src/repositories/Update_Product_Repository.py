from sqlalchemy.orm import Session
from src.models.product import Product, ProductSchema


class ProductUpdateRepository:

    def update_product(
        self,
        db: Session,
        product_data: ProductSchema,
        product_id: int | None = None,
        product_name: str | None = None
    ):
        """
        Updates a product by ID or name and returns the updated product.

        Returns None if no matching product is found.
        """
        if product_id is not None and product_name is not None:
            raise ValueError(
                "Provide either product_id or product_name, not both"
            )

        if product_id is not None:
            product = (
                db.query(Product)
                .filter(Product.id == product_id)
                .first()
            )

        elif product_name is not None:
            product = (
                db.query(Product)
                .filter(Product.name == product_name)
                .first()
            )

        else:
            return None

        if product is None:
            return None

        product.name = product_data.name
        product.unit = product_data.unit
        product.cost_per_unit = product_data.cost_per_unit
        product.price_per_unit = product_data.price_per_unit
        product.quantity_in_stock = product_data.quantity_in_stock

        db.commit()
        db.refresh(product)

        return product