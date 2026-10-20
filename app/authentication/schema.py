from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserSignup(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    phone_number: str | None = Field(default=None, max_length=20)
    country_code: str | None = Field(default=None, max_length=5)

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)