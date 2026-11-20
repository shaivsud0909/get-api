from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import Reviews
from app.reviews.schema import ReviewCreate, ReviewUpdate


async def _get_owned_review(db: AsyncSession, review_id: int, user_id: int) -> Reviews:
    stmt = select(Reviews).where(Reviews.id == review_id, Reviews.user_id == user_id)

    try:
        result = await db.execute(stmt)
        review = result.scalar_one_or_none()
    except Exception:
        raise

    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    return review


async def _get_review(db: AsyncSession, review_id: int) -> Reviews:
    try:
        result = await db.execute(select(Reviews).where(Reviews.id == review_id))
        review = result.scalar_one_or_none()
    except Exception:
        raise

    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    return review


async def create_review(product_id: int, user_id: int, data: ReviewCreate, db: AsyncSession):
    try:
        new_review = Reviews(
            product_id=product_id,
            user_id=user_id,
            rating=data.rating,
            comment=data.comment,
        )
        db.add(new_review)
        await db.commit()
        await db.refresh(new_review)
        return new_review
    except HTTPException:
        raise
    except Exception:
        await db.rollback()
        raise


async def get_reviews_by_product_id(db: AsyncSession, product_id: int):
    try:
        stmt = select(Reviews).where(Reviews.product_id == product_id)
        result = await db.execute(stmt)
        return result.scalars().all()
    except HTTPException:
        raise
    except Exception:
        raise


async def get_review_by_id(db: AsyncSession, review_id: int):
    try:
        return await _get_review(db, review_id)
    except HTTPException:
        raise
    except Exception:
        raise


async def update_review(db: AsyncSession, review_id: int, data: ReviewUpdate, user_id: int):
    try:
        review = await _get_owned_review(db, review_id, user_id)

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(review, key, value)

        await db.commit()
        await db.refresh(review)
        return review
    except HTTPException:
        raise
    except Exception:
        await db.rollback()
        raise


async def remove_review(db: AsyncSession, review_id: int, user_id: int):
    try:
        review = await _get_owned_review(db, review_id, user_id)

        await db.delete(review)
        await db.commit()
        return {"id": review_id}
    except HTTPException:
        raise
    except Exception:
        await db.rollback()
        raise



async def remove_review_admin(db: AsyncSession, review_id: int):
    try:
        review = await _get_review(db, review_id)

        await db.delete(review)
        await db.commit()
        return {"id": review_id}
    except HTTPException:
        raise
    except Exception:
        await db.rollback()
        raise