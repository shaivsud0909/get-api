from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.reviews.service import (
    create_review,
    get_review_by_id,
    get_reviews_by_product_id,
    remove_review,
    remove_review_admin,
    update_review,
)
from app.utils.api_response import api_response
from app.reviews.schema import ReviewCreate, ReviewUpdate


@api_response(success_message="Review added successfully", error_message="Failed to add review")
async def add_review(product_id: int, request: ReviewCreate, req: Request, db: Session = Depends(get_db)):
    try:
        current_user = req.state.user
        user_id = int(current_user["sub"])
        return await create_review(product_id=product_id, user_id=user_id, data=request, db=db)
    except HTTPException:
        raise
    except Exception:
        raise

@api_response(success_message="Review fetched successfully", error_message="Failed to fetch review")
async def fetch_reviews(product_id: int, db: Session = Depends(get_db)):
    try:
        return await get_reviews_by_product_id(db=db, product_id=product_id)
    except HTTPException:
        raise
    except Exception:
        raise

@api_response(success_message="Review fetched successfully", error_message="Failed to fetch review")
async def fetch_review(review_id: int, db: Session = Depends(get_db)):
    try:
        return await get_review_by_id(db=db, review_id=review_id)
    except HTTPException:
        raise
    except Exception:
        raise

@api_response(success_message="Review updated successfully", error_message="Failed to update review")
async def edit_review(review_id: int, request: ReviewUpdate, req: Request, db: Session = Depends(get_db)):
    try:
        current_user = req.state.user
        user_id = int(current_user["sub"])
        return await update_review(review_id=review_id, user_id=user_id, data=request, db=db)
    except HTTPException:
        raise
    except Exception:
        raise

@api_response(success_message="Review deleted successfully", error_message="Failed to delete review")
async def delete_review(review_id: int, req: Request, db: Session = Depends(get_db)):
    """Admins may delete any review; users may delete only their own."""
    try:
        user = req.state.user
        if user.get("role") == "admin":
            return await remove_review_admin(review_id=review_id, db=db)
        return await remove_review(review_id=review_id, user_id=int(user["sub"]), db=db)
    except HTTPException:
        raise
    except Exception:
        raise

