import enum

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
    Index,
    JSON,
    Enum,
)
from sqlalchemy.orm import relationship

from app.database.connection import Base


def _enum_values(enum_cls):
    # store the lowercase values ("pending_payment"), not the member names
    return [member.value for member in enum_cls]


class OrderStatus(str, enum.Enum):
    PENDING_PAYMENT = "pending_payment"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(str, enum.Enum):
    CREATED = "created"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


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
    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Reviews", back_populates="user", cascade="all, delete-orphan")


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    line1 = Column(String(200), nullable=False)
    line2 = Column(String(200), nullable=True)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=False)
    country = Column(String(100), nullable=False)
    is_default = Column(Boolean, nullable=False, default=False, server_default=text("false"))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="addresses")

    __table_args__ = (
        Index("uq_user_default_address", "user_id", unique=True, postgresql_where=text("is_default")),
    )


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
    reviews = relationship("Reviews", back_populates="product", cascade="all, delete-orphan")
    product_details = relationship("ProductDetails", back_populates="product", cascade="all, delete-orphan")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")


class ProductDetails(Base):
    __tablename__ = "product_details"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    key = Column(String(100), nullable=False)
    value = Column(String(300), nullable=False)
    detailed_description = Column(String(1000), nullable=True)

    product = relationship("Product", back_populates="product_details")

    __table_args__ = (
        UniqueConstraint("product_id", "key", name="uq_product_detail_key"),
    )


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    image_url = Column(String(500), nullable=False)
    alt_text = Column(String(200), nullable=True)
    is_primary = Column(Boolean, nullable=False, default=False)
    sort_order = Column(Integer, nullable=False, default=0)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    product = relationship("Product", back_populates="images")

    __table_args__ = (
        Index("uq_product_primary_image", "product_id", unique=True, postgresql_where=text("is_primary")),
    )


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


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    total_amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default="INR", server_default="INR")
    status = Column(
        Enum(OrderStatus, name="order_status", values_callable=_enum_values),
        nullable=False,
        default=OrderStatus.PENDING_PAYMENT,
    )
    shipping_address = Column(JSON, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True)
    product_name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)

    order = relationship("Order", back_populates="items")

    __table_args__ = (CheckConstraint("quantity > 0", name="ck_order_item_quantity"),)



class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    gateway = Column(String(20), nullable=False, default="razorpay")
    gateway_order_id = Column(String(100), nullable=False, unique=True)
    gateway_payment_id = Column(String(100), nullable=True)
    amount = Column(Integer, nullable=False)  # smallest currency unit (paise)
    currency = Column(String(3), nullable=False, default="INR")
    status = Column(
        Enum(PaymentStatus, name="payment_status", values_callable=_enum_values),
        nullable=False,
        default=PaymentStatus.CREATED,
    )
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    order = relationship("Order", back_populates="payments")

class Reviews(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)
    comment = Column(String(500), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    user = relationship("User",back_populates="reviews")
    product = relationship("Product",back_populates="reviews")

    __table_args__ = (
            CheckConstraint("rating >= 1 AND rating <= 5", name="ck_review_rating"),
            UniqueConstraint("user_id", "product_id", name="uq_user_product_review"),
        )
