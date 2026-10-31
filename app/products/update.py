from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Product
from app.products.schema import ProductUpdate


async def update_fields(
    product_id: int,
    data: ProductUpdate,
    db: AsyncSession,
):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update",
        )

    try:
        for field, value in update_data.items():
            setattr(product, field, value)

        await db.commit()
        await db.refresh(product)

    except Exception:
        await db.rollback()
        raise

    return product
