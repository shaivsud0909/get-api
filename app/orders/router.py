from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.authentication.role import user_required
from app.database.connection import get_db
from app.orders.checkout import checkout_service, get_order_service, get_orders_service
from app.orders.schema import CheckoutRequest
from app.utils.api_response import api_response


@api_response(success_message="Order created successfully", error_message="Failed to create order")
async def checkout(request: CheckoutRequest, current_user: dict = Depends(user_required), db: AsyncSession = Depends(get_db)):
    try:
        user_id = int(current_user["sub"])
        return await checkout_service(request.address_id, user_id, db)
    except HTTPException:
        raise
    except Exception:
        raise


@api_response(success_message="Orders fetched successfully", error_message="Failed to fetch orders")
async def fetch_orders(current_user: dict = Depends(user_required), db: AsyncSession = Depends(get_db)):
    try:
        user_id = int(current_user["sub"])
        return await get_orders_service(user_id, db)
    except HTTPException:
        raise
    except Exception:
        raise


@api_response(success_message="Order fetched successfully", error_message="Failed to fetch order")
async def fetch_order(order_id: int, current_user: dict = Depends(user_required), db: AsyncSession = Depends(get_db)):
    try:
        user_id = int(current_user["sub"])
        return await get_order_service(order_id, user_id, db)
    except HTTPException:
        raise
    except Exception:
        raise
