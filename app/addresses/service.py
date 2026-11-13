from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Address


async def _get_user_address(address_id: int, user_id: int, db: AsyncSession) -> Address:
    result = await db.execute(
        select(Address).where(Address.id == address_id, Address.user_id == user_id)
    )
    address = result.scalar_one_or_none()

    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found",
        )

    return address


async def create_address_service(data: dict, user_id: int, db: AsyncSession):
    has_address = await db.scalar(select(Address.id).where(Address.user_id == user_id).limit(1))

    address = Address(user_id=user_id, is_default=has_address is None, **data)

    try:
        db.add(address)
        await db.commit()
        await db.refresh(address)
    except Exception:
        await db.rollback()
        raise

    return address


async def get_addresses_service(user_id: int, db: AsyncSession):
    result = await db.execute(
        select(Address)
        .where(Address.user_id == user_id)
        .order_by(Address.is_default.desc(), Address.created_at.desc())
    )
    return result.scalars().all()


async def update_address_service(address_id: int, data: dict, user_id: int, db: AsyncSession):
    address = await _get_user_address(address_id, user_id, db)

    try:
        for field, value in data.items():
            setattr(address, field, value)

        await db.commit()
        await db.refresh(address)
    except Exception:
        await db.rollback()
        raise

    return address


async def select_address_service(address_id: int, user_id: int, db: AsyncSession):
    address = await _get_user_address(address_id, user_id, db)

    try:
        await db.execute(
            update(Address)
            .where(Address.user_id == user_id, Address.is_default.is_(True))
            .values(is_default=False)
        )
        address.is_default = True

        await db.commit()
        await db.refresh(address)
    except Exception:
        await db.rollback()
        raise

    return address


async def delete_address_service(address_id: int, user_id: int, db: AsyncSession):
    address = await _get_user_address(address_id, user_id, db)

    try:
        was_default = address.is_default
        await db.delete(address)
        await db.flush()

        if was_default:
            result = await db.execute(
                select(Address)
                .where(Address.user_id == user_id)
                .order_by(Address.created_at.desc())
                .limit(1)
            )
            next_default = result.scalar_one_or_none()
            if next_default:
                next_default.is_default = True

        await db.commit()
    except Exception:
        await db.rollback()
        raise

    return {"id": address_id}
