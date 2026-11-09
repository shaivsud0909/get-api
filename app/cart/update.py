from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Cart, CartItem, Product


async def update_cart_item_service(item_id: int, quantity: int, user_id: int, db: AsyncSession):
    result = await db.execute(
        select(CartItem)
        .join(Cart, Cart.id == CartItem.cart_id)
        .where(CartItem.id == item_id, Cart.user_id == user_id)
    )
    cart_item = result.scalar_one_or_none()

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found",
        )

    product_result = await db.execute(
        select(Product).where(Product.id == cart_item.product_id)
    )
    product = product_result.scalar_one_or_none()

    if product.stock < quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient product stock",
        )

    try:
        cart_item.quantity = quantity

        await db.commit()
        await db.refresh(cart_item)

        return cart_item

    except Exception:
        await db.rollback()
        raise
