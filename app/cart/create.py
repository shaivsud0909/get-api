from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Cart


async def create_cart(user_id: int, db: AsyncSession):
    new_cart = Cart(user_id=user_id)

    try:
        db.add(new_cart)
        await db.commit()
        await db.refresh(new_cart)
    except Exception:
        await db.rollback()
        raise

    return new_cart
