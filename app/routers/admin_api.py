from fastapi import APIRouter

from app.products.router import (
    add_product,
    add_product_features,
    add_product_image,
    delete_product_features,
    edit_product,
    fetch_product,
    fetch_product_features,
    fetch_products,
    remove_product,
    update_product_features,
)
from app.reviews.router import fetch_reviews,fetch_review, delete_review_admin

admin_router = APIRouter()

admin_router.post("/add-products")(add_product)
admin_router.get("/fetch-products")(fetch_products)

admin_router.get("/products/{product_id}")(fetch_product)
admin_router.patch("/products/{product_id}")(edit_product)
admin_router.delete("/products/{product_id}")(remove_product)

admin_router.post("/product-images/{product_id}")(add_product_image)

admin_router.post("/products-feature/{product_id}")(add_product_features)
admin_router.put("/products-feature/{product_id}/{feature_id}")(update_product_features)
admin_router.get("/products-feature/{product_id}")(fetch_product_features)
admin_router.delete("/products-feature/{product_id}")(delete_product_features)

admin_router.get("/products/{product_id}/reviews")(fetch_reviews)
admin_router.get("/reviews/{review_id}")(fetch_review)
admin_router.delete("/reviews/{review_id}")(delete_review_admin)


