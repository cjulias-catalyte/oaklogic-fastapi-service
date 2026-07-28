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
        return self.db.query(Product).all()

    def get_product_by_id(self, product_id: int) -> Product | None:
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_products_by_name(self, name: str) -> list[Product]:
        return self.db.query(Product).filter(Product.name.ilike(f"%{name}%")).all()

    def update_product(self, product_id: int, product_data: ProductSchema) -> Product | None:
        db_product = self.get_product_by_id(product_id)
        if not db_product:
            return None
        
        for key, value in product_data.model_dump().items():
            setattr(db_product, key, value)
            
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def delete_product(self, product_id: int) -> bool:
        db_product = self.get_product_by_id(product_id)
        if not db_product:
            return False
        self.db.delete(db_product)
        self.db.commit()
        return True

    def delete_products_by_name(self, name: str) -> bool:
        products = self.db.query(Product).filter(Product.name.ilike(name)).all()
        if not products:
            return False
        for product in products:
            self.db.delete(product)
        self.db.commit()
        return True