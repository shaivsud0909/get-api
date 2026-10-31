from fastapi import APIRouter

from app.products.router import fetch_products,fetch_customisable_products

user_router = APIRouter()

user_router.get("/products")(fetch_products)
user_router.get("customisable_products")(fetch_customisable_products)

