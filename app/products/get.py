
from typing import Literal

from sqlalchemy.orm import Session

from app.database.models import Product


def get_all_products(
    db: Session,
    category: str | None = None,
    order_by: Literal["id", "name", "price", "stock"] = "id",
    customisable: bool | None = None,
    order: Literal["asc", "desc"] = "asc",
):
    query = db.query(Product)

    if customisable is not None:
        query = query.filter(
            Product.customisable == customisable
        )

    if category:
        query = query.filter(
            Product.category.ilike(category)
        )

    column = getattr(Product, order_by)

    if order == "desc":
        query = query.order_by(column.desc())
    else:
        query = query.order_by(column.asc())

    return query.all()
