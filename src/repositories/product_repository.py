from src.models.product import Product, ProductSchema
from sqlalchemy.orm import Session


class ProductRepository:
    # def __init__(self):
    #     self._products: list[Product] = []

    # def add_product(self, product: Product) -> None:
    #     self._products.append(product)

   

    def __init__(self, db: Session):
        self.db = db
    
    def create_new_product(self, product_data: ProductSchema) -> Product:
        db_product = Product(
            id=product_data.id,
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
        return self.db.query(Product).all()
    
    def get_product_by_id(self, product_id: int) -> Product | None:
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_product_by_name(self, product_name: str) -> Product | None:
        return self.db.query(Product).filter(Product.name.ilike({product_name})).first()

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