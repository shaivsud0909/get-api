from pydantic import BaseModel, ConfigDict, Field


class Product(BaseModel):
    id: int
    name: str
    price: float
    stock: int
    category: str
    description: str | None = None
    customisable: bool

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(ge=0)
    stock: int = Field(default=0, ge=0)
    category: str = Field(default="Uncategorized", max_length=50)
    description: str | None = Field(default=None, max_length=300)
    customisable: bool = False


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    price: float | None = Field(default=None, ge=0)
    stock: int | None = Field(default=None, ge=0)
    category: str | None = Field(default=None, max_length=50)
    customisable: bool | None = None
    description: str | None = Field(default=None, max_length=300)
