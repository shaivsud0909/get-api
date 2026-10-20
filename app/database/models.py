from tkinter import Text

from sqlalchemy import TIMESTAMP, Boolean, Column, Integer, String, Float, text
from app.database.connection import Base





from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    TIMESTAMP,
    text,
    func,
)

from app.database.connection import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    phone_number = Column(String(20), nullable=True)
    country_code = Column(String(5), nullable=True)

    # Store a secure password hash, never a plaintext password
    password_hash = Column(String(255), nullable=False)

    role = Column(
        String(20),
        nullable=False,
        default="user"
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        
    )

    is_verified = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )

    is_deleted = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )

    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    last_login_at = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
    )




class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    category = Column(
        String(50),
        nullable=False,
        default="Uncategorized",
        index=True,
    )
    customisable = Column(Boolean, nullable=False, default=False)
    description = Column(String(300), nullable=True)

