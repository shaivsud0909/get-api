from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.authentication.role import user_required
from app.cart.add import add_to_cart_service
from app.cart.schema import AddToCart, UpdateCartItem
from app.database.connection import get_db
from app.cart.create import create_cart as create_cart_service
from app.cart.update import update_cart_item_service
from app.utils.api_response import api_response


@api_response(success_message="Cart created successfully", error_message="Failed to create cart")
async def create_cart(current_user: dict = Depends(user_required), db: AsyncSession = Depends(get_db)):
    try:
        user_id = int(current_user["sub"])
        return await create_cart_service(user_id,db)
    except HTTPException:
        raise
    except Exception:
        raise

@api_response(success_message="Added to cart successfully",error_message="Failed to add in cart")
async def add_to_cart(request:AddToCart,current_user: dict = Depends(user_required),db: AsyncSession = Depends(get_db)):
    try:
        user_id = int(current_user["sub"])
        return await add_to_cart_service(request.product_id,request.quantity,user_id,db)
    except HTTPException:
            raise
    except Exception:
            raise

@api_response(success_message="Cart item updated successfully", error_message="Failed to update cart item")
async def edit_cart_item(item_id: int, request: UpdateCartItem, current_user: dict = Depends(user_required), db: AsyncSession = Depends(get_db)):
    try:
        user_id = int(current_user["sub"])
        return await update_cart_item_service(item_id, request.quantity, user_id, db)
    except HTTPException:
        raise
    except Exception:
        raise
