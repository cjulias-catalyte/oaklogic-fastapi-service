from sqlalchemy.orm import Session

from src.models.product import Product, ProductCreate, ProductSchema


class ProductRepository:
    """Repository for performing database operations on Product objects."""
    def __init__(self, db: Session):
        """Initialize the repository with a database session.

        Args:
            db: An active SQLAlchemy database session.
        """
        self.db = db

    def create_new_product(self, product_data: ProductSchema) -> Product:
        """Create and persist a new product in the database.

        Args:
            product_data: The data required to create a new product.

        Returns:
            The newly created Product instance.
        """
        db_product = Product(
            name=product_data.name,
            unit=product_data.unit,
            cost_per_unit=product_data.cost_per_unit,
            price_per_unit=product_data.price_per_unit,
            quantity_in_stock=product_data.quantity_in_stock,
        )

        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)

        return db_product

    def get_all_products(self) -> list[Product]:
        """Retrieve all products from the database.

        Returns:
            A list of all Product objects.
        """
        return self.db.query(Product).all()

    def get_product_by_id(self, product_id: int) -> Product | None:
        """Retrieve a product by its unique ID.

        Args:
            product_id: The ID of the product to retrieve.

        Returns:
            The matching Product if found, otherwise None.
        """
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_product_by_name(self, product_name: str) -> Product | None:
        """Retrieve a product by its name.

        Performs a case-insensitive partial match on the product name.

        Args:
            product_name: The name or partial name of the product.

        Returns:
            The first matching Product if found, otherwise None.
        """
        return (
            self.db.query(Product)
            .filter(Product.name.ilike(f"%{product_name}%"))
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

        if name:
            query = query.filter(Product.name.ilike(f"%{name}%"))
        if unit:
            query = query.filter(Product.unit == unit)
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

    def delete_product_by_id(self, product_id: int) -> bool:
        """Delete a product by its unique ID.

        Args:
            product_id: The ID of the product to delete.

        Returns:
            True if the product was deleted successfully, otherwise False.
        """
        product = self.get_product_by_id(product_id)
        if not product:
            return False
        self.db.delete(product)
        self.db.commit()

        return True

    def delete_product_by_name(self, product_name: str) -> bool:
        """Delete a product by its name.

        Args:
            product_name: The name of the product to delete.

        Returns:
            True if the product was deleted successfully, otherwise False.
        """
        product = self.get_product_by_name(product_name)
        if product is None:
            return False
        self.db.delete(product)
        self.db.commit()

        return True


class ProductUpdateRepository:
    """Repository for updating existing Product objects."""

    def update_product(
        self,
        db: Session,
        product_data: ProductCreate | ProductSchema,
        product_id: int | None = None,
        product_name: str | None = None,
    ) -> Product | None:
        """Update an existing product by its ID or name.

        Exactly one of ``product_id`` or ``product_name`` must be provided.

        Args:
            db: An active SQLAlchemy database session.
            product_data: The updated product data.
            product_id: The ID of the product to update.
            product_name: The name of the product to update.

        Returns:
            The updated Product if found, otherwise None.

        Raises:
            ValueError: If both ``product_id`` and ``product_name`` are provided.
        """
        if product_id is not None and product_name is not None:
            raise ValueError(
                "Provide either product_id or product_name, not both"
            )

        if product_id is not None:
            product = repo.get_product_by_id(product_id)
        elif product_name is not None:
            product = repo.get_product_by_name(product_name)
        else:
            return None

        if not product:
            return None

        update_dict = product_data.model_dump(exclude_unset=True)
        update_dict.pop("id", None)

        cat_id = update_dict.get("category_id")
        if cat_id is not None and (not isinstance(cat_id, int) or cat_id <= 0):
            update_dict["category_id"] = None

        for key, value in update_dict.items():
            setattr(product, key, value)

        db.commit()
        db.refresh(product)
        return product