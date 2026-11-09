from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import User, Product, Cart, CartItem
from sqlalchemy import select



async def add_to_cart_service(product_id:int ,quantity:int ,user_id:int ,db:AsyncSession):
    try:
        product_result = await db.execute(
            select(Product).where(Product.id == product_id)
        )
        product = product_result.scalar_one_or_none()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )

        if product.stock < quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient product stock",
            )

        #find user cart
        cart_result = await db.execute(
            select(Cart).where(Cart.user_id == user_id)
        )
        cart = cart_result.scalar_one_or_none()

        #crete cart if not exsist
        if not cart:
            cart = Cart(user_id=user_id)
            db.add(cart)
            await db.flush()

        #check wether product already exsist in cart
        item_result = await db.execute(
            select(CartItem).where(
                CartItem.cart_id == cart.id,
                CartItem.product_id == product_id
            )
        )
        cart_item = item_result.scalar_one_or_none()

        if cart_item:
            new_quantity = cart_item.quantity + quantity

            if new_quantity > product.stock:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Requested quantity exceeds available stock",
                )

            cart_item.quantity = new_quantity

        else:
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=product_id,
                quantity=quantity
            )
            db.add(cart_item)

        await db.commit()
        await db.refresh(cart_item)

        return cart_item

    except HTTPException:
        await db.rollback()
        raise
    except Exception:
        await db.rollback()
        raise
