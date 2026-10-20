
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.database.models import Product


def delete_product(product_id: int, db: Session) -> None:
    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    try:
        db.delete(product)
        db.commit()
    except Exception:
        db.rollback()
        raise
