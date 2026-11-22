from fastapi import APIRouter

from app.products.router import fetch_product, fetch_product_features
from app.reviews.router import delete_review, fetch_review, fetch_reviews

# Routes open to both users and admins (guarded by any_role_required in main.py).
shared_router = APIRouter()

shared_router.get("/product/{product_id}")(fetch_product)
shared_router.get("/products/{product_id}")(fetch_product_features)

shared_router.get("/products/{product_id}/reviews")(fetch_reviews)
shared_router.get("/reviews/{review_id}")(fetch_review)
shared_router.delete("/reviews/{review_id}")(delete_review)
