from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.cart.add import add_to_cart_service
from app.cart.schema import AddToCart, UpdateCartItem
from app.database.connection import get_db
from app.cart.create import create_cart as create_cart_service
from app.cart.update import update_cart_item_service
from app.utils.api_response import api_response


@api_response(success_message="Cart created successfully", error_message="Failed to create cart")
async def create_cart(user_id: int, db: Session = Depends(get_db)):
    try:
        return await create_cart_service(user_id,db)
    except HTTPException:
        raise
    except Exception:
        raise

@api_response(success_message="Added to cart successfully",error_message="Failed to add in cart")
async def add_to_cart(request:AddToCart,user_id: int,db: Session = Depends(get_db)):
    try:
        return await add_to_cart_service(request.product_id,request.quantity,user_id,db)
    except HTTPException:
            raise
    except Exception:
            raise

@api_response(success_message="Cart item updated successfully", error_message="Failed to update cart item")
async def edit_cart_item(item_id: int, request: UpdateCartItem, user_id: int, db: Session = Depends(get_db)):
    try:
        return await update_cart_item_service(item_id, request.quantity, user_id, db)
    except HTTPException:
        raise
    except Exception:
        raise

