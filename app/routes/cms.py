from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid

from app.core.security import get_current_admin
from app.core.db import get_database

router = APIRouter()

# ---------------------------------------------------------
# PAGES CRUD
# ---------------------------------------------------------

@router.get("/pages")
async def list_pages(
    status: Optional[str] = None,
    type: Optional[str] = None,
    current_admin: dict = Depends(get_current_admin)
):
    """Get all CMS pages with optional filtering."""
    db = get_database()
    query = {}
    if status and status != 'All':
        query["status"] = status
    if type and type != 'All':
        query["type"] = type
        
    pages = await db["cms_pages"].find(query).sort("updated_at", -1).to_list(1000)
    for p in pages:
        p["_id"] = str(p["_id"])
    return pages

@router.post("/pages")
async def create_page(data: dict, current_admin: dict = Depends(get_current_admin)):
    """Create a new page."""
    db = get_database()
    
    doc = {
        "id": str(uuid.uuid4()),
        "title": data.get("title", "Untitled Page"),
        "slug": data.get("slug", ""),
        "type": data.get("type", "Custom"),
        "status": data.get("status", "Draft"),
        "content": data.get("content", []), # Blocks array
        "seo": data.get("seo", {}),
        "views": 0,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    await db["cms_pages"].insert_one(doc)
    doc["_id"] = str(doc["_id"])
    return doc

@router.put("/pages/{page_id}")
async def update_page(page_id: str, data: dict = Body(...), current_admin: dict = Depends(get_current_admin)):
    """Update page content/status."""
    db = get_database()
    
    update_data = {**data, "updated_at": datetime.now(timezone.utc)}
    # Remove _id if it was accidentally passed
    if "_id" in update_data:
        del update_data["_id"]
        
    res = await db["cms_pages"].update_one(
        {"id": page_id}, 
        {"$set": update_data}
    )
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Page not found")
    return {"message": "Page updated"}

@router.delete("/pages/{page_id}")
async def delete_page(page_id: str, current_admin: dict = Depends(get_current_admin)):
    """Delete a page."""
    db = get_database()
    res = await db["cms_pages"].delete_one({"id": page_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Page not found")
    return {"message": "Page deleted"}

# ---------------------------------------------------------
# THEME & SETTINGS
# ---------------------------------------------------------

@router.get("/theme")
async def get_theme_settings(current_admin: dict = Depends(get_current_admin)):
    db = get_database()
    theme = await db["cms_theme"].find_one({"id": "global_theme"})
    if not theme:
        return {
            "primaryColor": "#6366f1",
            "secondaryColor": "#4f46e5",
            "borderRadius": "xl",
            "fontFamily": "Inter"
        }
    theme["_id"] = str(theme["_id"])
    return theme

@router.post("/theme")
async def update_theme_settings(data: dict, current_admin: dict = Depends(get_current_admin)):
    db = get_database()
    await db["cms_theme"].update_one(
        {"id": "global_theme"},
        {"$set": data},
        upsert=True
    )
    return {"message": "Theme updated"}

# ---------------------------------------------------------
# ANALYTICS DASHBOARD
# ---------------------------------------------------------

@router.get("/analytics")
async def get_cms_analytics(current_admin: dict = Depends(get_current_admin)):
    db = get_database()
    total = await db["cms_pages"].count_documents({})
    published = await db["cms_pages"].count_documents({"status": "Published"})
    drafts = await db["cms_pages"].count_documents({"status": "Draft"})
    
    return {
        "total_pages": total,
        "published": published,
        "drafts": drafts,
        "storage_used_gb": 45.2,
        "seo_score": 92
    }
