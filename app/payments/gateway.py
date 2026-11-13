import hashlib
import hmac

import httpx
from fastapi import HTTPException, status

from core.config import settings

RAZORPAY_API = "https://api.razorpay.com/v1"


async def create_gateway_order(amount: int, currency: str, receipt: str) -> dict:
    """Create a Razorpay order. `amount` is in the smallest currency unit (paise)."""
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment gateway is not configured",
        )

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            f"{RAZORPAY_API}/orders",
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET),
            json={"amount": amount, "currency": currency, "receipt": receipt},
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Payment gateway rejected the request",
        )

    return response.json()


def verify_webhook_signature(body: bytes, signature: str | None) -> bool:
    if not settings.RAZORPAY_WEBHOOK_SECRET or not signature:
        return False

    expected = hmac.new(settings.RAZORPAY_WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
