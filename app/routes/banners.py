from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid

from app.core.security import get_current_admin
from app.core.db import get_database

router = APIRouter()

# ---------------------------------------------------------
# BANNER CRUD OPERATIONS
# ---------------------------------------------------------

@router.get("/")
async def list_banners(
    status: Optional[str] = None,
    banner_type: Optional[str] = None,
    search: Optional[str] = None,
    current_admin: dict = Depends(get_current_admin)
):
    """Get all banners with optional filtering."""
    db = get_database()
    query = {}
    
    if status and status != 'All':
        query["status"] = status
    if banner_type and banner_type != 'All':
        query["type"] = banner_type
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"campaign_name": {"$regex": search, "$options": "i"}}
        ]
        
    banners = await db["banners"].find(query).sort("created_at", -1).to_list(1000)
    for b in banners:
        b["_id"] = str(b["_id"])
    return banners

@router.get("/{banner_id}")
async def get_banner(banner_id: str, current_admin: dict = Depends(get_current_admin)):
    """Get a single banner."""
    db = get_database()
    banner = await db["banners"].find_one({"id": banner_id})
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")
    banner["_id"] = str(banner["_id"])
    return banner

@router.post("/")
async def create_banner(data: dict, current_admin: dict = Depends(get_current_admin)):
    """Create a new banner."""
    db = get_database()
    
    banner_doc = {
        "id": str(uuid.uuid4()),
        "title": data.get("title", "Untitled Banner"),
        "type": data.get("type", "Homepage Slider"),
        "status": data.get("status", "Draft"),
        "image_url": data.get("image_url", ""),
        "mobile_image_url": data.get("mobile_image_url", ""),
        "link": data.get("link", ""),
        "campaign_name": data.get("campaign_name", "None"),
        "start_date": data.get("start_date"),
        "end_date": data.get("end_date"),
        "target_pages": data.get("target_pages", ["Homepage"]),
        "target_customers": data.get("target_customers", "All"),
        "priority": int(data.get("priority", 0)),
        "views": 0,
        "clicks": 0,
        "conversions": 0,
        "revenue": 0.0,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    await db["banners"].insert_one(banner_doc)
    banner_doc["_id"] = str(banner_doc["_id"])
    return banner_doc

@router.put("/{banner_id}")
async def update_banner(banner_id: str, data: dict, current_admin: dict = Depends(get_current_admin)):
    """Update a banner."""
    db = get_database()
    
    existing = await db["banners"].find_one({"id": banner_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Banner not found")
        
    update_data = data.copy()
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    # Remove _id if present
    update_data.pop("_id", None)
    
    await db["banners"].update_one({"id": banner_id}, {"$set": update_data})
    
    updated = await db["banners"].find_one({"id": banner_id})
    updated["_id"] = str(updated["_id"])
    return updated

@router.delete("/{banner_id}")
async def delete_banner(banner_id: str, current_admin: dict = Depends(get_current_admin)):
    """Delete a banner."""
    db = get_database()
    res = await db["banners"].delete_one({"id": banner_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Banner not found")
    return {"message": "Banner deleted successfully"}

@router.put("/{banner_id}/status")
async def update_banner_status(banner_id: str, data: dict = Body(...), current_admin: dict = Depends(get_current_admin)):
    """Quickly pause, resume or schedule a banner."""
    db = get_database()
    status = data.get("status")
    if not status:
        raise HTTPException(status_code=400, detail="Status is required")
        
    res = await db["banners"].update_one(
        {"id": banner_id}, 
        {"$set": {"status": status, "updated_at": datetime.now(timezone.utc)}}
    )
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Banner not found")
    return {"message": f"Status updated to {status}"}

# ---------------------------------------------------------
# CAMPAIGN OPERATIONS
# ---------------------------------------------------------

@router.get("/campaigns/all")
async def list_campaigns(current_admin: dict = Depends(get_current_admin)):
    """List all campaigns."""
    db = get_database()
    campaigns = await db["campaigns"].find().sort("created_at", -1).to_list(1000)
    for c in campaigns:
        c["_id"] = str(c["_id"])
    return campaigns

@router.post("/campaigns")
async def create_campaign(data: dict, current_admin: dict = Depends(get_current_admin)):
    """Create a new campaign."""
    db = get_database()
    
    campaign_doc = {
        "id": str(uuid.uuid4()),
        "name": data.get("name"),
        "type": data.get("type", "General"),
        "status": data.get("status", "Draft"),
        "start_date": data.get("start_date"),
        "end_date": data.get("end_date"),
        "budget": float(data.get("budget", 0.0)),
        "created_at": datetime.now(timezone.utc)
    }
    
    await db["campaigns"].insert_one(campaign_doc)
    campaign_doc["_id"] = str(campaign_doc["_id"])
    return campaign_doc

# ---------------------------------------------------------
# ANALYTICS
# ---------------------------------------------------------

@router.get("/analytics/dashboard")
async def get_banner_analytics(current_admin: dict = Depends(get_current_admin)):
    """Aggregated stats for the KPI Dashboard."""
    db = get_database()
    
    # Global banner stats
    active_banners = await db["banners"].count_documents({"status": "Published"})
    scheduled_banners = await db["banners"].count_documents({"status": "Scheduled"})
    
    # Aggregate stats from all banners
    pipeline = [
        {"$group": {
            "_id": None,
            "total_views": {"$sum": "$views"},
            "total_clicks": {"$sum": "$clicks"},
            "total_conversions": {"$sum": "$conversions"},
            "total_revenue": {"$sum": "$revenue"}
        }}
    ]
    banner_stats = await db["banners"].aggregate(pipeline).to_list(1)
    
    stats = banner_stats[0] if banner_stats else {
        "total_views": 0,
        "total_clicks": 0,
        "total_conversions": 0,
        "total_revenue": 0
    }
    
    # Calculate CTR (Click Through Rate)
    ctr = (stats["total_clicks"] / stats["total_views"] * 100) if stats["total_views"] > 0 else 0
    
    # Calculate Conversion Rate
    cvr = (stats["total_conversions"] / stats["total_clicks"] * 100) if stats["total_clicks"] > 0 else 0
    
    # Top Banner
    top_banner = await db["banners"].find().sort("clicks", -1).limit(1).to_list(1)
    top_title = top_banner[0]["title"] if top_banner else "None"

    return {
        "active_count": active_banners,
        "scheduled_count": scheduled_banners,
        "total_banners": await db["banners"].count_documents({}),
        "total_views": stats["total_views"],
        "total_clicks": stats["total_clicks"],
        "total_revenue": stats["total_revenue"],
        "ctr": ctr,
        "cvr": cvr,
        "top_banner": top_title
    }
