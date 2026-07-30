from sqlalchemy.orm import Session, joinedload
from src.models.product import Category, CategoryCreate


class CategoryRepository:
    """Repository for performing database operations on Category objects."""

    def __init__(self, db: Session):
        self.db = db
        """Initialize the repository with a database session.

        Args:
            db: An active SQLAlchemy database session.
        """
    def create_category(self, category_data: CategoryCreate) -> Category:
        """Create and persist a new category in the database.

        Args:
            category_data: The data required to create a new category.

        Returns:
            The newly created Category instance.
        """
        db_category = Category(
            name=category_data.name,
            description=category_data.description,
        )
        self.db.add(db_category)
        self.db.commit()
        self.db.refresh(db_category)
        return db_category

    def get_all_categories(self) -> list[Category]:
        """Retrieve all categories from the database.

        Returns:
            A list of all Category objects.
        """
        return self.db.query(Category).all()

    def get_category_by_id(self, category_id: int) -> Category | None:
        """Retrieve a category by its unique ID.

        Args:
            category_id: The ID of the category to retrieve.

        Returns:
            The matching Category if found, otherwise None.
        """
        return (
            self.db.query(Category)
            .options(joinedload(Category.products))
            .filter(Category.id == category_id)
            .first()
        ) 