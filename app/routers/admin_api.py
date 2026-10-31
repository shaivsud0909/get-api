from fastapi import APIRouter

from app.products.router import (
    add_product,
    edit_product,
    fetch_product,
    fetch_products,
    remove_product,
)

admin_router = APIRouter()

admin_router.post("/products")(add_product)
admin_router.get("/products")(fetch_products)
admin_router.get("/products/{product_id}")(fetch_product)
admin_router.put("/products/{product_id}")(edit_product)
admin_router.delete("/products/{product_id}")(remove_product)
