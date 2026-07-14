from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from app.core.db import db
from app.core.security import get_current_admin
from datetime import datetime
from bson import ObjectId

router = APIRouter()

@router.get("/analytics")
async def get_reviews_analytics(current_admin: dict = Depends(get_current_admin)):
    """
    Get KPIs for Reviews Dashboard.
    """
    pipeline = [
        {
            "$group": {
                "_id": None,
                "total_reviews": {"$sum": 1},
                "published_reviews": {
                    "$sum": {"$cond": [{"$eq": ["$status", "Published"]}, 1, 0]}
                },
                "pending_reviews": {
                    "$sum": {"$cond": [{"$eq": ["$status", "Pending"]}, 1, 0]}
                },
                "rejected_reviews": {
                    "$sum": {"$cond": [{"$eq": ["$status", "Rejected"]}, 1, 0]}
                },
                "avg_rating": {"$avg": "$rating"},
                "5_star": {"$sum": {"$cond": [{"$eq": ["$rating", 5]}, 1, 0]}},
                "4_star": {"$sum": {"$cond": [{"$eq": ["$rating", 4]}, 1, 0]}},
                "3_star": {"$sum": {"$cond": [{"$eq": ["$rating", 3]}, 1, 0]}},
                "2_star": {"$sum": {"$cond": [{"$eq": ["$rating", 2]}, 1, 0]}},
                "1_star": {"$sum": {"$cond": [{"$eq": ["$rating", 1]}, 1, 0]}}
            }
        }
    ]
    
    result = await db["reviews"].aggregate(pipeline).to_list(1)
    
    # Calculate some extra dummy/trend fields for UI demonstration
    # In real world, we'd query by date for today vs yesterday
    if result:
        data = result[0]
        data.pop("_id", None)
        # Adding AI insights mock data
        data["sentiment_breakdown"] = {
            "positive": int(data["total_reviews"] * 0.7),
            "neutral": int(data["total_reviews"] * 0.2),
            "negative": int(data["total_reviews"] * 0.1)
        }
        data["growth"] = 12.5 # Fake growth %
        return data
    else:
        return {
            "total_reviews": 0,
            "published_reviews": 0,
            "pending_reviews": 0,
            "rejected_reviews": 0,
            "avg_rating": 0,
            "5_star": 0, "4_star": 0, "3_star": 0, "2_star": 0, "1_star": 0,
            "sentiment_breakdown": {"positive": 0, "neutral": 0, "negative": 0},
            "growth": 0
        }

@router.get("")
async def get_all_reviews(
    status: Optional[str] = None,
    rating: Optional[int] = None,
    search: Optional[str] = None,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Get all reviews with filters for Admin Manager.
    """
    query = {}
    if status and status != "All":
        query["status"] = status
    if rating:
        query["rating"] = rating
        
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"review_text": {"$regex": search, "$options": "i"}},
            {"user_name": {"$regex": search, "$options": "i"}},
            {"product_id": {"$regex": search, "$options": "i"}},
        ]
        
    reviews_cursor = db["reviews"].find(query).sort("created_at", -1)
    reviews_list = await reviews_cursor.to_list(1000)
    
    # Add product name for better UI display (using aggregation would be better, but doing it in python for speed of setup if small dataset)
    # To keep it performant, we might want to fetch unique product names. For now, returning raw.
    return reviews_list

@router.put("/{review_id}/status")
async def update_review_status(
    review_id: str, 
    status: str = Query(..., description="Status: Published, Rejected, Pending, Archived"),
    current_admin: dict = Depends(get_current_admin)
):
    """
    Approve, Reject or Archive a review.
    """
    result = await db["reviews"].update_one(
        {"_id": review_id}, 
        {"$set": {"status": status}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"message": f"Review {status}", "review_id": review_id}

@router.put("/{review_id}/reply")
async def update_review_reply(
    review_id: str, 
    payload: dict,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Admin writes a public reply.
    """
    reply = payload.get("admin_reply")
    result = await db["reviews"].update_one(
        {"_id": review_id}, 
        {"$set": {"admin_reply": reply}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"message": "Reply updated"}

@router.put("/{review_id}/notes")
async def update_review_notes(
    review_id: str, 
    payload: dict,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Admin writes an internal private note.
    """
    note = payload.get("internal_notes")
    result = await db["reviews"].update_one(
        {"_id": review_id}, 
        {"$set": {"internal_notes": note}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"message": "Notes updated"}

@router.delete("/{review_id}")
async def delete_review(
    review_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Delete a review completely.
    """
    result = await db["reviews"].delete_one({"_id": review_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"message": "Review deleted"}

@router.post("/run-ai-moderation")
async def run_ai_moderation(current_admin: dict = Depends(get_current_admin)):
    """
    Mock endpoint that simulates AI reading all 'Pending' reviews and assigning sentiment/status.
    """
    # Find all pending
    cursor = db["reviews"].find({"status": "Pending"})
    async for review in cursor:
        text = review.get("review_text", "").lower()
        
        # Super naive AI mock
        sentiment = "Neutral"
        status = "Pending"
        
        if any(word in text for word in ["great", "awesome", "good", "love", "perfect"]):
            sentiment = "Positive"
            status = "Published"
        elif any(word in text for word in ["bad", "terrible", "worst", "hate", "fake"]):
            sentiment = "Negative"
            status = "Rejected" # Flagged
            
        await db["reviews"].update_one(
            {"_id": review["_id"]},
            {"$set": {"sentiment": sentiment, "status": status}}
        )
        
    return {"message": "AI Moderation completed on pending reviews."}
