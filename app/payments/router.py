from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.authentication.role import user_required
from app.database.connection import get_db
from app.payments.schema import InitiatePayment
from app.payments.service import handle_webhook_service, initiate_payment_service
from app.utils.api_response import api_response


@api_response(success_message="Payment initiated successfully", error_message="Failed to initiate payment")
async def initiate_payment(request: InitiatePayment, current_user: dict = Depends(user_required), db: AsyncSession = Depends(get_db)):
    try:
        user_id = int(current_user["sub"])
        return await initiate_payment_service(request.order_id, user_id, db)
    except HTTPException:
        raise
    except Exception:
        raise


@api_response(success_message="Webhook processed", error_message="Failed to process webhook")
async def payment_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        body = await request.body()
        signature = request.headers.get("X-Razorpay-Signature")
        return await handle_webhook_service(body, signature, db)
    except HTTPException:
        raise
    except Exception:
        raise
