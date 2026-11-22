from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.addresses.service import _get_user_address
from app.database.models import Cart, CartItem, Order, OrderItem, OrderStatus, Product
from core.config import settings


def serialize_order(order: Order) -> dict:
    """Items must be eager loaded; lazy loading is unavailable on async sessions.

    Returning the ORM object as-is recurses forever: OrderItem.order points back
    at this same Order, and FastAPI's jsonable_encoder walks relationships.
    """
    return {
        "id": order.id,
        "total_amount": order.total_amount,
        "currency": order.currency,
        "status": order.status,
        "shipping_address": order.shipping_address,
        "created_at": order.created_at,
        "items": [
            {
                "product_id": i.product_id,
                "product_name": i.product_name,
                "price": i.price,
                "quantity": i.quantity,
            }
            for i in order.items
        ],
    }


async def checkout_service(address_id: int, user_id: int, db: AsyncSession):
    address = await _get_user_address(address_id, user_id, db)

    result = await db.execute(
        select(CartItem, Product)
        .join(Cart, Cart.id == CartItem.cart_id)
        .join(Product, Product.id == CartItem.product_id)
        .where(Cart.user_id == user_id)
    )
    rows = result.all()

    if not rows:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")

    total = Decimal("0")
    order_items = []
    for cart_item, product in rows:
        if product.stock < cart_item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {product.name}",
            )
        total += Decimal(str(product.price)) * cart_item.quantity
        order_items.append(
            OrderItem(
                product_id=product.id,
                product_name=product.name,
                price=product.price,
                quantity=cart_item.quantity,
            )
        )

    order = Order(
        user_id=user_id,
        total_amount=float(total.quantize(Decimal("0.01"))),
        currency=settings.PAYMENT_CURRENCY,
        status=OrderStatus.PENDING_PAYMENT,
        shipping_address={
            "full_name": address.full_name,
            "phone": address.phone,
            "line1": address.line1,
            "line2": address.line2,
            "city": address.city,
            "state": address.state,
            "postal_code": address.postal_code,
            "country": address.country,
        },
        items=order_items,
    )

    try:
        db.add(order)
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    return serialize_order(order)


async def get_orders_service(user_id: int, db: AsyncSession):
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
    )
    return [serialize_order(order) for order in result.scalars().all()]


async def get_order_service(order_id: int, user_id: int, db: AsyncSession):
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == order_id, Order.user_id == user_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    return serialize_order(order)
