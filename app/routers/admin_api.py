from fastapi import APIRouter

from app.products.router import (
    add_product,
    add_product_features,
    delete_product_features,
    edit_product,
    fetch_product_features,
    fetch_products,
    remove_product,
    update_product_features,
)

admin_router = APIRouter()

admin_router.post("/add-products")(add_product)
admin_router.get("/fetch-products")(fetch_products)
admin_router.patch("/products/{product_id}")(edit_product)
admin_router.delete("/products/{product_id}")(remove_product)

admin_router.post("/products-feature/{product_id}")(add_product_features)
admin_router.put("/products-feature/{product_id}/{feature_id}")(update_product_features)
admin_router.get("/products-feature/{product_id}")(fetch_product_features)
admin_router.delete("/products-feature/{product_id}")(delete_product_features)



