from pydantic import BaseModel, ConfigDict, Field, model_validator


class Product(BaseModel):
    id: int
    name: str
    price: float
    original_price: float | None = None
    stock: int
    category: str
    description: str | None = None
    customisable: bool

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(ge=0)
    original_price: float | None = Field(default=None, ge=0)
    stock: int = Field(default=0, ge=0)
    category: str = Field(default="Uncategorized", max_length=50)
    description: str | None = Field(default=None, max_length=300)
    customisable: bool = False

    @model_validator(mode="after")
    def check_original_price(self):
        if self.original_price is not None and self.original_price < self.price:
            raise ValueError("original_price must be greater than or equal to price")
        return self


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    price: float | None = Field(default=None, ge=0)
    original_price: float | None = Field(default=None, ge=0)
    stock: int | None = Field(default=None, ge=0)
    category: str | None = Field(default=None, max_length=50)
    customisable: bool | None = None
    description: str | None = Field(default=None, max_length=300)

class ProductFeatures(BaseModel):
    key: str = Field(..., min_length=1, max_length=100)
    value: str = Field(..., min_length=1, max_length=300)
    detailed_description: str | None = Field(default=None, max_length=1000)

class ProductImage(BaseModel):
    alt_text: str | None = Field(default=None, max_length=200)
    is_primary: bool = False

class ProductImageResponse(BaseModel):
    sort_order: int