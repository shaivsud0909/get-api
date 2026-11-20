from pydantic import BaseModel, Field
from typing import Optional



class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating must be between 1 and 5")
    comment: Optional[str] = Field(None, max_length=500, description="Optional comment for the review")

class ReviewUpdate(BaseModel):
    rating: int = Field(None, ge=1, le=5, description="Rating must be between 1 and 5")
    comment: Optional[str] = Field(None, max_length=500, description="Optional comment for the review")