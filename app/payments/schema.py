from pydantic import BaseModel


class InitiatePayment(BaseModel):
    order_id: int
