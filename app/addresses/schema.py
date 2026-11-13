from typing import Optional

from pydantic import BaseModel, Field


class AddressCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=100)
    phone: str = Field(min_length=5, max_length=20)
    line1: str = Field(min_length=1, max_length=200)
    line2: Optional[str] = Field(default=None, max_length=200)
    city: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=1, max_length=100)
    postal_code: str = Field(min_length=1, max_length=20)
    country: str = Field(min_length=1, max_length=100)


class AddressUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    phone: Optional[str] = Field(default=None, min_length=5, max_length=20)
    line1: Optional[str] = Field(default=None, min_length=1, max_length=200)
    line2: Optional[str] = Field(default=None, max_length=200)
    city: Optional[str] = Field(default=None, min_length=1, max_length=100)
    state: Optional[str] = Field(default=None, min_length=1, max_length=100)
    postal_code: Optional[str] = Field(default=None, min_length=1, max_length=20)
    country: Optional[str] = Field(default=None, min_length=1, max_length=100)
