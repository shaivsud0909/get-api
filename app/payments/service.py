import json
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Cart, CartItem, Order, Payment, Product
from app.payments.gateway import create_gateway_order, verify_webhook_signature
from core.config import settings
from core.logs import logger


def _to_minor_units(amount: float) -> int:
    return int((Decimal(str(amount)) * 100).quantize(Decimal("1")))


async def initiate_payment_service(order_id: int, user_id: int, db: AsyncSession):
    result = await db.execute(
        select(Order).where(Order.id == order_id, Order.user_id == user_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    if order.status != "pending_payment":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order is not awaiting payment")

    # amount always comes from the stored order, never from the client
    amount = _to_minor_units(order.total_amount)

    # reuse an unpaid gateway order so retries don't create duplicates
    existing = await db.execute(
        select(Payment).where(
            Payment.order_id == order.id,
            Payment.status == "created",
            Payment.amount == amount,
        )
    )
    payment = existing.scalars().first()

    if not payment:
        gateway_order = await create_gateway_order(amount, order.currency, f"order_{order.id}")
        payment = Payment(
            order_id=order.id,
            user_id=user_id,
            gateway="razorpay",
            gateway_order_id=gateway_order["id"],
            amount=amount,
            currency=order.currency,
            status="created",
        )
        try:
            db.add(payment)
            await db.commit()
        except Exception:
            await db.rollback()
            raise

    return {
        "order_id": order.id,
        "payment_id": payment.id,
        "gateway": payment.gateway,
        "gateway_order_id": payment.gateway_order_id,
        "key_id": settings.RAZORPAY_KEY_ID,
        "amount": payment.amount,
        "currency": payment.currency,
    }


async def _fulfil_order(order: Order, db: AsyncSession):
    for item in order.items:
        if item.product_id is not None:
            await db.execute(
                update(Product)
                .where(Product.id == item.product_id)
                .values(stock=Product.stock - item.quantity)
            )

    # clear the buyer's cart now that the purchase is confirmed
    cart_id = await db.scalar(select(Cart.id).where(Cart.user_id == order.user_id))
    if cart_id is not None:
        await db.execute(delete(CartItem).where(CartItem.cart_id == cart_id))


async def handle_webhook_service(body: bytes, signature: str | None, db: AsyncSession):
    if not verify_webhook_signature(body, signature):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")

    event = json.loads(body)
    event_type = event.get("event")

    if event_type not in ("payment.captured", "order.paid", "payment.failed"):
        return {"handled": False}

    entity = event["payload"]["payment"]["entity"]
    gateway_order_id = entity.get("order_id")

    # row lock so concurrent gateway retries are processed one at a time
    result = await db.execute(
        select(Payment).where(Payment.gateway_order_id == gateway_order_id).with_for_update()
    )
    payment = result.scalar_one_or_none()

    if not payment:
        logger.warning("Webhook for unknown gateway order %s", gateway_order_id)
        return {"handled": False}

    if payment.status == "paid":
        return {"handled": True, "duplicate": True}

    try:
        if event_type == "payment.failed":
            # the gateway lets the customer retry on the same order, so keep it open
            payment.gateway_payment_id = entity.get("id")
        else:
            if entity.get("amount") != payment.amount or entity.get("currency") != payment.currency:
                logger.error("Amount mismatch for gateway order %s", gateway_order_id)
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount mismatch")

            order = await db.scalar(select(Order).where(Order.id == payment.order_id).with_for_update())
            await db.refresh(order, ["items"])

            payment.status = "paid"
            payment.gateway_payment_id = entity.get("id")
            order.status = "confirmed"
            await _fulfil_order(order, db)

        await db.commit()
    except Exception:
        await db.rollback()
        raise

    return {"handled": True}
