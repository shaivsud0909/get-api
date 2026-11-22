from typing import Literal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Product
from app.products.schema import ProductCreate, ProductUpdate


async def _get_product(db: AsyncSession, product_id: int) -> Product:
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    return product


async def create_products(request: ProductCreate, db: AsyncSession):
    new_product = Product(
        name=request.name,
        price=request.price,
        original_price=request.original_price,
        stock=request.stock,
        category=request.category,
        customisable=request.customisable,
        description=request.description,
    )

    try:
        db.add(new_product)
        await db.commit()
        await db.refresh(new_product)
    except Exception:
        await db.rollback()
        raise

    return new_product


async def get_all_products(
    db: AsyncSession,
    category: str | None = None,
    order_by: Literal["id", "name", "price", "stock"] = "id",
    customisable: bool | None = None,
    order: Literal["asc", "desc"] = "asc",
):
    try:
        stmt = select(Product)

        if customisable is not None:
            stmt = stmt.where(Product.customisable == customisable)

        if category:
            stmt = stmt.where(Product.category.ilike(category))

        column = getattr(Product, order_by)

        if order == "desc":
            stmt = stmt.order_by(column.desc())
        else:
            stmt = stmt.order_by(column.asc())

        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception:
        raise


async def search_product(db: AsyncSession, product_id: int):
    return await _get_product(db, product_id)


async def update_fields(product_id: int, data: ProductUpdate, db: AsyncSession):
    product = await _get_product(db, product_id)

    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    new_price = update_data.get("price", product.price)
    new_original_price = update_data.get("original_price", product.original_price)
    if new_original_price is not None and new_original_price < new_price:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="original_price must be greater than or equal to price",
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


async def delete_product(product_id: int, db: AsyncSession) -> None:
    product = await _get_product(db, product_id)

    try:
        await db.delete(product)
        await db.commit()
    except Exception:
        await db.rollback()
        raise
