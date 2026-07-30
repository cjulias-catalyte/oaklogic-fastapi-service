from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from src.database import Base


# ==========================================
# PYDANTIC SCHEMAS
# ==========================================
class ProductCreate(BaseModel):
    name: str
    unit: str
    cost_per_unit: float = Field(gt=0)
    price_per_unit: float = Field(gt=0)
    quantity_in_stock: float = Field(ge=0)
    category_id: int | None = None


class ProductSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    name: str
    unit: str
    cost_per_unit: float = Field(gt=0)
    price_per_unit: float = Field(gt=0)
    quantity_in_stock: float = Field(ge=0)
    category_id: int | None = None


class CategoryCreate(BaseModel):
    name: str
    description: str | None = None


class CategorySchema(BaseModel):
    """Returns a category WITH its nested list of products."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    products: list[ProductSchema] = []


# ==========================================
# SQLALCHEMY ORM MODELS
# ==========================================
class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)

    # One-to-Many: One Category has many Products
    products = relationship(
        "Product",
        back_populates="category",
        cascade="all, delete-orphan",
    )


class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    unit = Column(String, index=True, nullable=False)
    cost_per_unit = Column(Float, index=True, nullable=False)
    price_per_unit = Column(Float, index=True, nullable=False)
    quantity_in_stock = Column(Float, index=True, nullable=False)

    # Foreign Key pointing to category.id (nullable=True allows uncategorized products)
    category_id = Column(
        Integer,
        ForeignKey("category.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
    )

    # Many-to-One: Many Products belong to one Category
    category = relationship("Category", back_populates="products")