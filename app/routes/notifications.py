from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid

from app.core.security import get_current_admin
from app.core.db import get_database

router = APIRouter()

# ---------------------------------------------------------
# NOTIFICATIONS CRUD
# ---------------------------------------------------------

@router.get("/")
async def list_notifications(
    channel: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_admin: dict = Depends(get_current_admin)
):
    """Get all notifications with optional filtering."""
    db = get_database()
    query = {}
    
    if channel and channel != 'All':
        query["channel"] = channel
    if status and status != 'All':
        query["status"] = status
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"campaign": {"$regex": search, "$options": "i"}}
        ]
        
    notifications = await db["notifications"].find(query).sort("created_at", -1).to_list(1000)
    for n in notifications:
        n["_id"] = str(n["_id"])
    return notifications

@router.post("/")
async def create_notification(data: dict, current_admin: dict = Depends(get_current_admin)):
    """Create a new notification campaign."""
    db = get_database()
    
    doc = {
        "id": str(uuid.uuid4()),
        "title": data.get("title", "Untitled Notification"),
        "channel": data.get("channel", "Email"), # Email, SMS, WhatsApp, Push, In-App
        "status": data.get("status", "Draft"), # Draft, Scheduled, Sending, Completed, Failed
        "audience": data.get("audience", "All"),
        "content": data.get("content", ""),
        "campaign": data.get("campaign", "None"),
        "scheduled_for": data.get("scheduled_for", None),
        "sent_count": 0,
        "delivered_count": 0,
        "failed_count": 0,
        "opened_count": 0,
        "clicked_count": 0,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    await db["notifications"].insert_one(doc)
    doc["_id"] = str(doc["_id"])
    return doc

@router.put("/{notification_id}/status")
async def update_notification_status(notification_id: str, data: dict = Body(...), current_admin: dict = Depends(get_current_admin)):
    """Update notification status."""
    db = get_database()
    status = data.get("status")
    if not status:
        raise HTTPException(status_code=400, detail="Status is required")
        
    res = await db["notifications"].update_one(
        {"id": notification_id}, 
        {"$set": {"status": status, "updated_at": datetime.now(timezone.utc)}}
    )
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": f"Status updated to {status}"}

# ---------------------------------------------------------
# WORKFLOW AUTOMATION ENGINE
# ---------------------------------------------------------

@router.get("/workflows")
async def list_workflows(current_admin: dict = Depends(get_current_admin)):
    """Get all automation workflows."""
    db = get_database()
    workflows = await db["workflows"].find().sort("created_at", -1).to_list(100)
    for w in workflows:
        w["_id"] = str(w["_id"])
    return workflows

@router.post("/workflows")
async def create_workflow(data: dict, current_admin: dict = Depends(get_current_admin)):
    """Save an automation workflow."""
    db = get_database()
    doc = {
        "id": str(uuid.uuid4()),
        "name": data.get("name", "Untitled Workflow"),
        "trigger": data.get("trigger", "Order Created"),
        "nodes": data.get("nodes", []), # Contains visual node tree structure
        "status": data.get("status", "Active"),
        "created_at": datetime.now(timezone.utc)
    }
    await db["workflows"].insert_one(doc)
    doc["_id"] = str(doc["_id"])
    return doc

# ---------------------------------------------------------
# ANALYTICS
# ---------------------------------------------------------

@router.get("/analytics/dashboard")
async def get_notification_analytics(current_admin: dict = Depends(get_current_admin)):
    """Aggregated stats for the KPI Dashboard."""
    db = get_database()
    
    # Global stats
    total_notifications = await db["notifications"].count_documents({})
    scheduled = await db["notifications"].count_documents({"status": "Scheduled"})
    failed = await db["notifications"].count_documents({"status": "Failed"})
    
    pipeline = [
        {"$group": {
            "_id": None,
            "total_sent": {"$sum": "$sent_count"},
            "total_delivered": {"$sum": "$delivered_count"},
            "total_opened": {"$sum": "$opened_count"},
            "total_clicked": {"$sum": "$clicked_count"},
            "total_failed": {"$sum": "$failed_count"},
        }}
    ]
    stats_list = await db["notifications"].aggregate(pipeline).to_list(1)
    stats = stats_list[0] if stats_list else {
        "total_sent": 0, "total_delivered": 0, "total_opened": 0, 
        "total_clicked": 0, "total_failed": 0
    }
    
    # Calculate rates
    delivery_rate = (stats["total_delivered"] / stats["total_sent"] * 100) if stats["total_sent"] > 0 else 0
    open_rate = (stats["total_opened"] / stats["total_delivered"] * 100) if stats["total_delivered"] > 0 else 0
    click_rate = (stats["total_clicked"] / stats["total_opened"] * 100) if stats["total_opened"] > 0 else 0

    return {
        "total_campaigns": total_notifications,
        "scheduled_campaigns": scheduled,
        "failed_campaigns": failed,
        "total_sent": stats["total_sent"],
        "total_delivered": stats["total_delivered"],
        "total_opened": stats["total_opened"],
        "total_failed": stats["total_failed"],
        "delivery_rate": delivery_rate,
        "open_rate": open_rate,
        "click_rate": click_rate
    }
