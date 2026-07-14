from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ReviewBase(BaseModel):
    product_id: str
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = None
    review_text: str
    images: List[str] = []
    videos: List[str] = []
    is_verified_purchase: bool = False

class ReviewCreate(ReviewBase):
    pass

class ReviewInDB(ReviewBase):
    id: str = Field(alias="_id")
    user_id: str
    user_name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Moderation & Enterprise fields
    status: str = "Pending"  # Pending, Published, Rejected, Archived
    admin_reply: Optional[str] = None
    internal_notes: Optional[str] = None
    sentiment: str = "Neutral"  # Positive, Neutral, Negative
    is_featured: bool = False
    helpful_votes: int = 0
    reported: bool = False
    
    # Fraud tracking
    device: Optional[str] = None
    location: Optional[str] = None
    ip_address: Optional[str] = None

    model_config = {"populate_by_name": True}

class ReviewResponse(ReviewInDB):
    model_config = {"populate_by_name": True, "from_attributes": True}
