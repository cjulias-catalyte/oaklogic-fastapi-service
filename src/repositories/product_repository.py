from sqlalchemy.orm import Session

from src.models.product import Product, ProductSchema


class ProductRepository:
    """Repository for creating, retrieving, searching, and deleting products."""

    def __init__(self, db: Session):
        """Initialize the repository with an active database session.

        Args:
            db: An active SQLAlchemy database session.
        """
        self.db = db

    def create_new_product(self, product_data: ProductSchema) -> Product:
        """Create and save a new product in the database.

        Args:
            product_data: Validated product data used to create the product.

        Returns:
            The newly created Product database object.
        """
        db_product = Product(
            name=product_data.name,
            unit=product_data.unit,
            cost_per_unit=product_data.cost_per_unit,
            price_per_unit=product_data.price_per_unit,
            quantity_in_stock=product_data.quantity_in_stock,
            category_id=product_data.category_id,
        )

        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)

        return db_product

    def get_all_products(self) -> list[Product]:
        """Retrieve every product stored in the database.

        Returns:
            A list containing all Product objects.
        """
        return self.db.query(Product).all()

    def get_product_by_id(self, product_id: int) -> Product | None:
        """Retrieve one product by its unique ID.

        Args:
            product_id: The ID of the product to retrieve.

        Returns:
            The matching Product if found, otherwise None.
        """
        return (
            self.db.query(Product)
            .filter(Product.id == product_id)
            .first()
        )

    def get_product_by_name(self, product_name: str) -> Product | None:
        """Retrieve one product using a case-insensitive exact name match.

        Leading and trailing spaces are removed before the query is run.

        Args:
            product_name: The full name of the product to retrieve.

        Returns:
            The matching Product if found, otherwise None.
        """
        return (
            self.db.query(Product)
            .filter(Product.name.ilike(product_name.strip()))
            .first()
        )

    def get_product_by_exact_name(
        self,
        product_name: str,
    ) -> Product | None:
        """Retrieve one product using a case-insensitive exact name match.

        This method is used when an operation, such as deletion, should only
        occur when the complete product name is provided.

        Args:
            product_name: The complete product name.

        Returns:
            The matching Product if found, otherwise None.
        """
        return (
            self.db.query(Product)
            .filter(Product.name.ilike(product_name.strip()))
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

        Product names use a case-insensitive partial match. Units use a
        case-insensitive match. Numeric fields require exact matches.

        Args:
            name: Optional partial product name.
            unit: Optional unit of measurement.
            cost_per_unit: Optional exact cost per unit.
            price_per_unit: Optional exact price per unit.
            quantity_in_stock: Optional exact stock quantity.

        Returns:
            A list of products matching all supplied filters.
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
        """Find all products containing the supplied name text.

        The search is case-insensitive and uses a partial name match.

        Args:
            product_name: A full or partial product name.

        Returns:
            A list of all products whose names contain the supplied text.
        """
        return (
            self.db.query(Product)
            .filter(
                Product.name.ilike(
                    f"%{product_name.strip()}%"
                )
            )
            .all()
        )

    def delete_product_by_id(self, product_id: int) -> bool:
        """Delete a product using its unique ID.

        Args:
            product_id: The ID of the product to delete.

        Returns:
            True if the product was found and deleted.
            False if no matching product was found.
        """
        product = self.get_product_by_id(product_id)

        if product is None:
            return False

        self.db.delete(product)
        self.db.commit()

        return True

    def delete_product_by_name(self, product_name: str) -> bool:
        """Delete a product using its complete name.

        The deletion uses a case-insensitive exact name match.

        Args:
            product_name: The complete name of the product to delete.

        Returns:
            True if the product was found and deleted.
            False if no matching product was found.
        """
        product = self.get_product_by_exact_name(product_name)

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
        product_data: ProductSchema,
        product_id: int | None = None,
        product_name: str | None = None,
    ) -> Product | None:
        """Update an existing product by ID or name.

        Exactly one identifier should be provided. The method performs a full
        update of the product's name, unit, cost, price, and stock quantity.

        Args:
            db: An active SQLAlchemy database session.
            product_data: Validated replacement data for the product.
            product_id: The ID of the product to update.
            product_name: The name of the product to update.

        Returns:
            The updated Product if found, otherwise None.

        Raises:
            ValueError: If both product_id and product_name are provided.
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

        # The primary key is not updated because it identifies the
        # existing database row.
        product.name = product_data.name
        product.unit = product_data.unit
        product.cost_per_unit = product_data.cost_per_unit
        product.price_per_unit = product_data.price_per_unit
        product.quantity_in_stock = product_data.quantity_in_stock

        db.commit()
        db.refresh(product)

        return product