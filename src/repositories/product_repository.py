from sqlalchemy.orm import Session
from src.models.product import Product, ProductSchema


class ProductRepository:

    def __init__(self, db: Session):
        self.db = db

    def create_new_product(self, product_data: ProductSchema) -> Product:
        # Convert Pydantic model to dict
        data = product_data.model_dump(exclude_unset=True)

        # Remove id if present so database auto-generates primary key
        data.pop("id", None)

        # Normalize category_id: if 0 or invalid, set to None
        if data.get("category_id") == 0:
            data["category_id"] = None

        db_product = Product(**data)
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def get_all_products(self) -> list[Product]:
        return self.db.query(Product).all()

    def get_product_by_id(self, product_id: int) -> Product | None:
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_product_by_name(self, name: str) -> Product | None:
        return self.db.query(Product).filter(Product.name == name).first()

    def search_products(
        self,
        name: str | None = None,
        unit: str | None = None,
        cost_per_unit: float | None = None,
        price_per_unit: float | None = None,
        quantity_in_stock: float | None = None,
    ) -> list[Product]:
        query = self.db.query(Product)

        if name:
            query = query.filter(Product.name.ilike(f"%{name}%"))
        if unit:
            query = query.filter(Product.unit == unit)
        if cost_per_unit is not None:
            query = query.filter(Product.cost_per_unit == cost_per_unit)
        if price_per_unit is not None:
            query = query.filter(Product.price_per_unit == price_per_unit)
        if quantity_in_stock is not None:
            query = query.filter(Product.quantity_in_stock == quantity_in_stock)

        return query.all()

    def delete_product_by_id(self, product_id: int) -> bool:
        product = self.get_product_by_id(product_id)
        if not product:
            return False
        self.db.delete(product)
        self.db.commit()
        return True

    def delete_product_by_name(self, name: str) -> bool:
        product = self.get_product_by_name(name)
        if not product:
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
        repo = ProductRepository(db)

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

        if update_dict.get("category_id") == 0:
            update_dict["category_id"] = None

        for key, value in update_dict.items():
            setattr(product, key, value)

        db.commit()
        db.refresh(product)
        return product