from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.review import ReviewCreate, ReviewResponse, ReviewInDB
from app.core.security import get_current_user
from app.models.user import UserInDB
from app.core.db import get_database
from datetime import datetime
import uuid

router = APIRouter()

def _serialize(doc: dict) -> dict:
    if doc is None:
        return None
    d = dict(doc)
    if "_id" in d:
        d["_id"] = str(d["_id"])
    return d

@router.get("/{product_id}/can-review")
async def check_can_review(product_id: str, current_user: dict = Depends(get_current_user)):
    db = get_database()
    user_id = current_user["id"]
    
    # Check if they have already reviewed
    existing = await db["reviews"].find_one({"product_id": product_id, "user_id": user_id})
    if existing:
        return {"can_review": False, "reason": "You have already reviewed this product."}
        
    # Check if they have purchased the product
    has_purchased = await db["orders"].find_one({
        "user_id": user_id, 
        "items.product_id": product_id,
        "order_status": {"$ne": "Cancelled"}  # Must not be a cancelled order
    })
    
    if not has_purchased:
        return {"can_review": False, "reason": "You can only review products you have purchased."}
        
    return {"can_review": True, "reason": ""}

@router.get("/{product_id}", response_model=List[ReviewResponse])
async def get_reviews(product_id: str):
    db = get_database()
    raw = await db["reviews"].find({"product_id": product_id}).sort("created_at", -1).to_list(1000)
    return [_serialize(r) for r in raw]

@router.post("", response_model=ReviewResponse)
async def create_review(review_in: ReviewCreate, current_user: dict = Depends(get_current_user)):
    db = get_database()
    user_id = current_user["id"]
    
    # Verify purchase
    has_purchased = await db["orders"].find_one({
        "user_id": user_id, 
        "items.product_id": review_in.product_id,
        "order_status": {"$ne": "Cancelled"}
    })
    if not has_purchased:
        raise HTTPException(status_code=403, detail="You can only review products you have purchased.")

    # Check if already reviewed
    existing = await db["reviews"].find_one({"product_id": review_in.product_id, "user_id": user_id})
    if existing:
        raise HTTPException(status_code=400, detail="You have already reviewed this product")

    user = await db["users"].find_one({"_id": user_id})
    user_name = user.get("full_name", "Anonymous") if user else "Anonymous"

    review_dict = review_in.model_dump()
    review_dict["_id"] = str(uuid.uuid4())
    review_dict["user_id"] = user_id
    review_dict["user_name"] = user_name
    review_dict["created_at"] = datetime.utcnow()

    db_review = ReviewInDB(**review_dict)
    await db["reviews"].insert_one(db_review.model_dump(by_alias=True))
    
    return db_review
