
# app/products/product_router.py

from typing import Literal

from fastapi import Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Product
from app.products.schema import ProductCreate, ProductUpdate
from app.products.create import create_products
from app.products.get import get_all_products
from app.products.update import update_fields
from app.products.delete import delete_product



def add_product(
    request: ProductCreate,
    db: Session = Depends(get_db),
):
    return create_products(request, db)


def fetch_products(
    category: str | None = None,
    customisable: bool | None = None,
    order_by: Literal["id", "name", "price", "stock"] = "id",
    order: Literal["asc", "desc"] = "asc",
    db: Session = Depends(get_db),
):
    return get_all_products(
        db=db,
        category=category,
        customisable=customisable,
        order_by=order_by,
        order=order,
    )


def fetch_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return product



def edit_product(
    product_id: int,
    request: ProductUpdate,
    db: Session = Depends(get_db),
):
    return update_fields(
        product_id=product_id,
        data=request,
        db=db,
    )



def remove_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    delete_product(product_id, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
