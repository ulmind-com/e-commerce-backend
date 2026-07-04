from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ReviewBase(BaseModel):
    product_id: str
    rating: int = Field(..., ge=1, le=5)
    review_text: str

class ReviewCreate(ReviewBase):
    pass

class ReviewInDB(ReviewBase):
    id: str = Field(alias="_id")
    user_id: str
    user_name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"populate_by_name": True}

class ReviewResponse(ReviewInDB):
    model_config = {"populate_by_name": True, "from_attributes": True}
