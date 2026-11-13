from fastapi import APIRouter

from app.payments.router import payment_webhook

payment_router = APIRouter()

# public: authenticated by the gateway's HMAC signature, not a user token
payment_router.post("/payments/webhook")(payment_webhook)
