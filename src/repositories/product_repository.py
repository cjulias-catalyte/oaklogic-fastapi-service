from sqlalchemy.orm import Session
from src.models.product import Product, ProductSchema

class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_new_product(self, product_data: ProductSchema) -> Product:
        db_product = Product(**product_data.model_dump())
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def get_all_products(self) -> list[Product]:
        return self.db.query(Product).filter(Product.is_active == True).all()

    def get_product_by_id(self, product_id: int) -> Product | None:
        return self.db.query(Product).filter(Product.id == product_id, Product.is_active == True).first()

    def get_product_by_name(self, product_name: str) -> Product | None:
        return self.db.query(Product).filter(Product.name.ilike(f"%{product_name}%")).first()
    
    def search_products(
        self,
        name: str | None = None,
        unit: str | None = None,
        cost_per_unit: float | None = None,
        price_per_unit: float | None = None,
        quantity_in_stock: float | None = None,
    ) -> list[Product]:
        query = self.db.query(Product)

        if name is not None:
            query = query.filter(Product.name.ilike(f"%{name}%"))
        if unit is not None:
            query = query.filter(Product.unit.ilike(unit))
        if cost_per_unit is not None:
            query = query.filter(Product.cost_per_unit == cost_per_unit)
        if price_per_unit is not None:
            query = query.filter(Product.price_per_unit == price_per_unit)
        if quantity_in_stock is not None:
            query = query.filter(Product.quantity_in_stock == quantity_in_stock)

        return query.all()

    def get_product_by_id(
        self,
        product_id: int,
    ) -> Product | None:
        return (
            self.db.query(Product)
            .filter(Product.id == product_id)
            .first()
        )

    def delete_product_by_id(
        self,
        product_id: int,
    ) -> bool:
        product = self.get_product_by_id(product_id)

        if product is None:
            return False

        self.db.delete(product)
        self.db.commit()

        return True

    def delete_product_by_name(
            self,
            product_name: str,
        ) -> bool:
            product = self.get_product_by_name(product_name)
    
            if product is None:
                return False
    
            self.db.delete(product)
            self.db.commit()
    
            return True