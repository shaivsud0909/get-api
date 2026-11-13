from pydantic import BaseModel


class CheckoutRequest(BaseModel):
    address_id: int
