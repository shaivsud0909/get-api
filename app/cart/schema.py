from pydantic import BaseModel, Field

class AddToCart(BaseModel):
    product_id:int
    quantity:int


class UpdateCartItem(BaseModel):
    quantity: int = Field(ge=1)