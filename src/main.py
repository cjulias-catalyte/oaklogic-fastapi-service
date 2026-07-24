from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from src.database import engine, Base, SessionLocal
from sqlalchemy.orm import Session
from src.models.product import Product
from src.repositories.product_repository import ProductRepository

app = FastAPI()
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

products = ProductRepository()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello, {name}!"}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    count = db.query(Product).count()
    return {"product_count": count}