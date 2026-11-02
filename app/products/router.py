# app/products/product_router.py

from typing import Literal

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Product
from app.products.schema import ProductCreate, ProductUpdate
from app.products.create import create_products
from app.products.get import get_all_products, search_product
from app.products.update import update_fields
from app.products.delete import delete_product
from app.utils.api_response import api_response


@api_response(success_message="Product added successfully", error_message="Failed to add product")
async def add_product(request: ProductCreate, db: Session = Depends(get_db)):
    try:
        return await create_products(request, db)
    except HTTPException:
        raise
    except Exception:
        raise


@api_response(success_message="Products fetched successfully", error_message="Failed to fetch products")
async def fetch_products(category: str | None = None, customisable: bool | None = None, order_by: Literal["id", "name", "price", "stock"] = "id", order: Literal["asc", "desc"] = "asc", db: Session = Depends(get_db)):
    try:
        return await get_all_products(db=db, category=category, customisable=customisable, order_by=order_by, order=order)
    except HTTPException:
        raise
    except Exception:
        raise


@api_response(success_message="Customisable products fetched successfully", error_message="Failed to fetch customisable products")
async def fetch_customisable_products(category: str | None = None, customisable: bool = True, order_by: Literal["id", "name", "price", "stock"] = "id", order: Literal["asc", "desc"] = "asc", db: Session = Depends(get_db)):
    try:
        return await get_all_products(db=db, category=category, customisable=customisable, order_by=order_by, order=order)
    except HTTPException:
        raise
    except Exception:
        raise


@api_response(success_message="Product fetched successfully", error_message="Failed to fetch product")
async def fetch_product(product_id: int, db: Session = Depends(get_db)):
    try:
        return await search_product(db=db, product_id=product_id)
    except HTTPException:
        raise
    except Exception:
        raise


@api_response(success_message="Product updated successfully", error_message="Failed to update product")
async def edit_product(product_id: int, request: ProductUpdate, db: Session = Depends(get_db)):
    try:
        return await update_fields(product_id=product_id, data=request, db=db)
    except HTTPException:
        raise
    except Exception:
        raise


@api_response(success_message="Product deleted successfully", error_message="Failed to delete product")
async def remove_product(product_id: int, db: Session = Depends(get_db)):
    try:
        return await delete_product(product_id, db)
    except HTTPException:
        raise
    except Exception:
        raise
