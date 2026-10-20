from alembic.environment import Optional
from pydantic import BaseModel, Field


class Product(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None
    customisable: bool


class ProductUpdate(BaseModel):
    name: str | None = None
    price: float | None = Field(default=None, ge=0)
    stock: int | None = Field(default=None, ge=0)
    category: str | None = None
    customisable: bool | None = None
    description: str | None = None