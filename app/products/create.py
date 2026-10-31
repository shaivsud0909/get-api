from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Product
from app.products.schema import ProductCreate


async def create_products(request: ProductCreate, db: AsyncSession):
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
        await db.commit()
        await db.refresh(new_product)
    except Exception:
        await db.rollback()
        raise

    return new_product
