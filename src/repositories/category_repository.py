from sqlalchemy.orm import Session
from src.models.product import Category, CategoryCreate


class CategoryRepository:

    def __init__(self, db: Session):
        self.db = db

    def create_category(self, category_data: CategoryCreate) -> Category:
        db_category = Category(
            name=category_data.name,
            description=category_data.description,
        )
        self.db.add(db_category)
        self.db.commit()
        self.db.refresh(db_category)
        return db_category

    def get_all_categories(self) -> list[Category]:
        return self.db.query(Category).all()

    def get_category_by_id(self, category_id: int) -> Category | None:
        return (
            self.db.query(Category)
            .filter(Category.id == category_id)
            .first()
        ) 
    
    def delete_category_by_id(self, category_id: int) -> Category | None:
        """Delete a category by its ID.

        Args:
            category_id: The ID of the category to delete.

        Returns:
            The deleted Category if it existed, otherwise None.
        """
        category = self.db.query(Category).filter(Category.id == category_id).first()

        if category is None:
            return None

        self.db.delete(category)
        self.db.commit()
        return category
