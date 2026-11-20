from fastapi import APIRouter

from app.products.router import fetch_product, fetch_product_features, fetch_products,fetch_customisable_products
from app.cart.router import create_cart,add_to_cart,edit_cart_item
from app.addresses.router import add_address,fetch_addresses,edit_address,select_address,remove_address
from app.orders.router import checkout,fetch_orders,fetch_order
from app.payments.router import initiate_payment
from app.reviews.router import add_review, delete_review, edit_review, fetch_review, fetch_reviews

user_router = APIRouter()

user_router.get("/products")(fetch_products)
user_router.get("/product/{product_id}")(fetch_product)
user_router.get("/customisable-products")(fetch_customisable_products)

user_router.get("/products/{product_id}")(fetch_product_features)

user_router.get("/products/{product_id}/reviews")(fetch_reviews)
user_router.post("/products/{product_id}/reviews")(add_review)

user_router.get("/reviews/{review_id}")(fetch_review)
user_router.put("/reviews/{review_id}")(edit_review)
user_router.delete("/reviews/{review_id}")(delete_review)

user_router.get("/cart")(create_cart)
user_router.post("/add-to-cart")(add_to_cart)
user_router.patch("/cart-item/{item_id}")(edit_cart_item)

user_router.post("/addresses")(add_address)
user_router.get("/addresses")(fetch_addresses)
user_router.put("/addresses/{address_id}")(edit_address)
user_router.patch("/addresses/{address_id}/select")(select_address)
user_router.delete("/addresses/{address_id}")(remove_address)

user_router.post("/checkout")(checkout)
user_router.get("/orders")(fetch_orders)
user_router.get("/orders/{order_id}")(fetch_order)

user_router.post("/payments/initiate")(initiate_payment)
