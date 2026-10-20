
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.models import Product
from app.products.schema import ProductUpdate


def update_fields(
    product_id: int,
    data: ProductUpdate,
    db: Session,
):
    product = (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    # Only include fields provided by the admin
    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update",
        )

    try:
        for field, value in update_data.items():
            setattr(product, field, value)

        db.commit()
        db.refresh(product)

    except Exception:
        db.rollback()
        raise

    return product
