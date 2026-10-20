
from sqlalchemy.orm import Session

from app.database.models import Product
from app.products.schema import ProductCreate


def create_products(request: ProductCreate, db: Session):
    new_product = Product(
        name=request.name,
        price=request.price,
        stock=request.stock,
        category=request.category,
        customisable=request.customisable,
        description=request.description,
    )

    try:
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
    except Exception:
        db.rollback()
        raise

    return new_product
