from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.addresses.schema import AddressCreate, AddressUpdate
from app.addresses.service import (
    create_address_service,
    delete_address_service,
    get_addresses_service,
    select_address_service,
    update_address_service,
)
from app.authentication.role import user_required
from app.database.connection import get_db
from app.utils.api_response import api_response


@api_response(success_message="Address added successfully", error_message="Failed to add address")
async def add_address(request: AddressCreate, current_user: dict = Depends(user_required), db: AsyncSession = Depends(get_db)):
    try:
        user_id = int(current_user["sub"])
        return await create_address_service(request.model_dump(), user_id, db)
    except HTTPException:
        raise
    except Exception:
        raise


@api_response(success_message="Addresses fetched successfully", error_message="Failed to fetch addresses")
async def fetch_addresses(current_user: dict = Depends(user_required), db: AsyncSession = Depends(get_db)):
    try:
        user_id = int(current_user["sub"])
        return await get_addresses_service(user_id, db)
    except HTTPException:
        raise
    except Exception:
        raise


@api_response(success_message="Address updated successfully", error_message="Failed to update address")
async def edit_address(address_id: int, request: AddressUpdate, current_user: dict = Depends(user_required), db: AsyncSession = Depends(get_db)):
    try:
        user_id = int(current_user["sub"])
        return await update_address_service(address_id, request.model_dump(exclude_unset=True), user_id, db)
    except HTTPException:
        raise
    except Exception:
        raise


@api_response(success_message="Address selected successfully", error_message="Failed to select address")
async def select_address(address_id: int, current_user: dict = Depends(user_required), db: AsyncSession = Depends(get_db)):
    try:
        user_id = int(current_user["sub"])
        return await select_address_service(address_id, user_id, db)
    except HTTPException:
        raise
    except Exception:
        raise


@api_response(success_message="Address deleted successfully", error_message="Failed to delete address")
async def remove_address(address_id: int, current_user: dict = Depends(user_required), db: AsyncSession = Depends(get_db)):
    try:
        user_id = int(current_user["sub"])
        return await delete_address_service(address_id, user_id, db)
    except HTTPException:
        raise
    except Exception:
        raise
