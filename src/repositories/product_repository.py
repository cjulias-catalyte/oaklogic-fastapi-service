from sqlalchemy import func
from sqlalchemy.orm import Session
from src.models.product import Product, ProductSchema


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_new_product(self, product_data: ProductSchema) -> Product:
        db_product = Product(
            name=product_data.name,
            unit=product_data.unit,
            cost_per_unit=product_data.cost_per_unit,
            price_per_unit=product_data.price_per_unit,
            quantity_in_stock=product_data.quantity_in_stock,
            category_id=product_data.category_id
        )

        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)

        return db_product

    def get_all_products(self) -> list[Product]:
        return self.db.query(Product).all()

    def get_product_by_id(self, product_id: int) -> Product | None:
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_product_by_name(self, product_name: str) -> Product | None:
        return (
            self.db.query(Product)
            .filter(Product.name.ilike(f"%{product_name}%"))
            .first()
        )

    def get_product_by_exact_name(self, product_name: str) -> Product | None:
        """Retrieve a product using an exact, case-insensitive name match."""
        cleaned_name = product_name.strip()
        if not cleaned_name:
            return None

        return (
            self.db.query(Product)
            .filter(func.lower(Product.name) == cleaned_name.lower())
            .first()
        )

    def search_products(
            self,
            name: str | None = None,
            unit: str | None = None,
            cost_per_unit: float | None = None,
            price_per_unit: float | None = None,
            quantity_in_stock: float | None = None,
        ) -> list[Product]:
        """Search for products using one or more optional filters.

        Args:
            name: Filter by product name (case-insensitive partial match).
            unit: Filter by unit of measurement.
            cost_per_unit: Filter by cost per unit.
            price_per_unit: Filter by price per unit.
            quantity_in_stock: Filter by quantity in stock.

        Returns:
            A list of products matching the specified filters.
        """
        query = self.db.query(Product)

        if name is not None:
            query = query.filter(Product.name.ilike(f"%{name}%"))
        if unit is not None:
            query = query.filter(Product.unit.ilike(unit))
        if cost_per_unit is not None:
            query = query.filter(
                Product.cost_per_unit == cost_per_unit
            )

        if price_per_unit is not None:
            query = query.filter(
                Product.price_per_unit == price_per_unit
            )

        if quantity_in_stock is not None:
            query = query.filter(
                Product.quantity_in_stock == quantity_in_stock
            )

        return query.all()

    def search_products_by_name(
            self,
            product_name: str,
    ) -> list[Product]:
        """Return products containing the provided name."""
        if not product_name or not product_name.strip():
            return []

        cleaned_name = product_name.strip()

        return (
            self.db.query(Product)
            .filter(Product.name.ilike(f"%{cleaned_name}%"))
            .all()
        )

    def delete_product_by_id(self, product_id: int) -> bool:
        product = self.get_product_by_id(product_id)
        if product is None:
            return False

        self.db.delete(product)
        self.db.commit()

        return True

    def delete_product_by_name(self, product_name: str) -> bool:
        product = self.get_product_by_name(product_name)
        if product is None:
            return False

        self.db.delete(product)
        self.db.commit()

        return True


class ProductUpdateRepository:
    def update_product(
        self,
        db: Session,
        product_data: ProductSchema,
        product_id: int | None = None,
        product_name: str | None = None,
    ) -> Product | None:
        if product_id is not None and product_name is not None:
            raise ValueError(
                "Provide either product_id or product_name, not both"
            )

        repo = ProductRepository(db)
        if product_id is not None:
            product = db.query(Product).filter(Product.id == product_id).first()
        elif product_name is not None:
            product = db.query(Product).filter(Product.name == product_name).first()
        else:
            return None

        if product is None:
            return None

        # Primary key mutation removed so PostgreSQL / Pydantic None checks pass
        product.name = product_data.name
        product.unit = product_data.unit
        product.cost_per_unit = product_data.cost_per_unit
        product.price_per_unit = product_data.price_per_unit
        product.quantity_in_stock = product_data.quantity_in_stock

        db.commit()
        db.refresh(product)
        return product

    