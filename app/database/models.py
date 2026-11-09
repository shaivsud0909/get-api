from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    TIMESTAMP,
    Float,
    text,
    func,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.orm import relationship

from app.database.connection import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone_number = Column(String(20), nullable=True)
    country_code = Column(String(5), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="user")
    is_active = Column(Boolean, nullable=False, default=True)
    is_verified = Column(Boolean, nullable=False, default=False, server_default=text("false"))
    is_deleted = Column(Boolean, nullable=False, default=False, server_default=text("false"))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column( TIMESTAMP(timezone=True), nullable=False, server_default=func.now(),onupdate=func.now(),)
    last_login_at = Column(TIMESTAMP(timezone=True), nullable=True)

    cart = relationship("Cart",back_populates="user",uselist=False,cascade="all, delete-orphan")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    category = Column(String(50), nullable=False,default="Uncategorized",index=True,)
    customisable = Column(Boolean, nullable=False, default=False)
    description = Column(String(300), nullable=True)

    cart_items = relationship("CartItem", back_populates="product", cascade="all, delete-orphan")


class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer,ForeignKey("users.id", ondelete="CASCADE"),nullable=False,unique=True,index=True)
    created_at = Column(TIMESTAMP(timezone=True),nullable=False, server_default=func.now() )
    updated_at = Column( TIMESTAMP(timezone=True),nullable=False,server_default=func.now(),onupdate=func.now())

    user = relationship("User", back_populates="cart")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)

    cart_id = Column(Integer,ForeignKey("carts.id", ondelete="CASCADE"),nullable=False,index=True)
    product_id = Column(Integer,ForeignKey("products.id", ondelete="CASCADE"),nullable=False,index=True)
    quantity = Column(Integer,nullable=False,default=1)
    created_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default=func.now(),onupdate=func.now())

    cart = relationship("Cart",back_populates="items")
    product = relationship("Product",back_populates="cart_items")

    __table_args__ = (
        UniqueConstraint("cart_id", "product_id", name="uq_cart_product"),
        CheckConstraint("quantity > 0", name="ck_cart_item_quantity"),
    )
