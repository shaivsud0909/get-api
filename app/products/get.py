from typing import Literal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Product


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



async def search_product(
    db: AsyncSession,
    product_id: int,
):
    stmt = select(Product).where(Product.id == product_id)

    result = await db.execute(stmt)
    return result.scalar_one_or_none()