from fastapi import APIRouter

from app.products.router import fetch_products,fetch_customisable_products
from app.cart.router import create_cart,add_to_cart,edit_cart_item

user_router = APIRouter()

user_router.get("/products")(fetch_products)
user_router.get("/customisable-products")(fetch_customisable_products)

user_router.get("/cart")(create_cart)
user_router.post("/add-to-cart")(add_to_cart)
user_router.patch("/cart-item/{item_id}")(edit_cart_item)


