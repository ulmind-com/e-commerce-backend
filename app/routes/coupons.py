from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid

from app.core.security import get_current_admin
from app.core.db import get_database

router = APIRouter()

# ---------------------------------------------------------
# COUPON CRUD OPERATIONS
# ---------------------------------------------------------

@router.get("/")
async def list_coupons(
    status: Optional[str] = None,
    coupon_type: Optional[str] = None,
    search: Optional[str] = None,
    current_admin: dict = Depends(get_current_admin)
):
    """Get all coupons with optional filtering."""
    db = get_database()
    query = {}
    
    if status and status != 'All':
        query["status"] = status
    if coupon_type and coupon_type != 'All':
        query["type"] = coupon_type
    if search:
        query["$or"] = [
            {"code": {"$regex": search, "$options": "i"}},
            {"name": {"$regex": search, "$options": "i"}}
        ]
        
    coupons = await db["coupons"].find(query).sort("created_at", -1).to_list(1000)
    for c in coupons:
        c["_id"] = str(c["_id"])
    return coupons

@router.get("/{coupon_id}")
async def get_coupon(coupon_id: str, current_admin: dict = Depends(get_current_admin)):
    """Get a single coupon."""
    db = get_database()
    coupon = await db["coupons"].find_one({"id": coupon_id})
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    coupon["_id"] = str(coupon["_id"])
    return coupon

@router.post("/")
async def create_coupon(data: dict, current_admin: dict = Depends(get_current_admin)):
    """Create a new coupon."""
    db = get_database()
    
    # Check if code exists
    existing = await db["coupons"].find_one({"code": data.get("code", "").upper()})
    if existing:
        raise HTTPException(status_code=400, detail="Coupon code already exists")
        
    coupon_doc = {
        "id": str(uuid.uuid4()),
        "code": data.get("code", "").upper(),
        "name": data.get("name"),
        "description": data.get("description", ""),
        "type": data.get("type", "percentage"),
        "discount_value": float(data.get("discount_value", 0)),
        "min_cart_value": float(data.get("min_cart_value", 0)),
        "max_discount": float(data.get("max_discount", 0)),
        "start_date": data.get("start_date"),
        "end_date": data.get("end_date"),
        "usage_limit": int(data.get("usage_limit", 0)),
        "per_customer_limit": int(data.get("per_customer_limit", 1)),
        "status": data.get("status", "Active"),
        "visibility": data.get("visibility", "Public"),
        "applicable_products": data.get("applicable_products", []),
        "applicable_categories": data.get("applicable_categories", []),
        "applicable_brands": data.get("applicable_brands", []),
        "customer_targeting": data.get("customer_targeting", "all"),
        "payment_rules": data.get("payment_rules", "all"),
        "auto_apply": data.get("auto_apply", False),
        "stackable": data.get("stackable", False),
        "priority": int(data.get("priority", 0)),
        "usage_count": 0,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    await db["coupons"].insert_one(coupon_doc)
    coupon_doc["_id"] = str(coupon_doc["_id"])
    return coupon_doc

@router.put("/{coupon_id}")
async def update_coupon(coupon_id: str, data: dict, current_admin: dict = Depends(get_current_admin)):
    """Update a coupon."""
    db = get_database()
    
    existing = await db["coupons"].find_one({"id": coupon_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Coupon not found")
        
    # Prevent duplicate code on update
    if "code" in data and data["code"].upper() != existing["code"]:
        code_check = await db["coupons"].find_one({"code": data["code"].upper()})
        if code_check:
            raise HTTPException(status_code=400, detail="Coupon code already exists")
            
    update_data = data.copy()
    update_data["updated_at"] = datetime.now(timezone.utc)
    if "code" in update_data:
        update_data["code"] = update_data["code"].upper()
        
    # Remove _id if present in payload
    update_data.pop("_id", None)
    
    await db["coupons"].update_one({"id": coupon_id}, {"$set": update_data})
    
    updated = await db["coupons"].find_one({"id": coupon_id})
    updated["_id"] = str(updated["_id"])
    return updated

@router.delete("/{coupon_id}")
async def delete_coupon(coupon_id: str, current_admin: dict = Depends(get_current_admin)):
    """Delete a coupon."""
    db = get_database()
    res = await db["coupons"].delete_one({"id": coupon_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Coupon not found")
    return {"message": "Coupon deleted successfully"}

@router.put("/{coupon_id}/status")
async def update_coupon_status(coupon_id: str, data: dict = Body(...), current_admin: dict = Depends(get_current_admin)):
    """Quickly pause, resume or expire a coupon."""
    db = get_database()
    status = data.get("status")
    if not status:
        raise HTTPException(status_code=400, detail="Status is required")
        
    res = await db["coupons"].update_one(
        {"id": coupon_id}, 
        {"$set": {"status": status, "updated_at": datetime.now(timezone.utc)}}
    )
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Coupon not found")
    return {"message": f"Status updated to {status}"}

# ---------------------------------------------------------
# ANALYTICS
# ---------------------------------------------------------

@router.get("/analytics/dashboard")
async def get_coupon_analytics(current_admin: dict = Depends(get_current_admin)):
    """Aggregated stats for the KPI Dashboard."""
    db = get_database()
    
    # Global coupon stats
    active_coupons = await db["coupons"].count_documents({"status": "Active"})
    expired_coupons = await db["coupons"].count_documents({"status": "Expired"})
    scheduled_coupons = await db["coupons"].count_documents({"status": "Scheduled"})
    
    # Revenue and usage stats (Mocked logic for now, typically joined with Orders collection where coupon_code is present)
    # Since we need a robust dashboard immediately, we calculate some simulated metrics if order data is sparse
    
    pipeline = [
        {"$match": {"coupon_code": {"$exists": True, "$ne": None}}},
        {"$group": {
            "_id": None,
            "total_usage": {"$sum": 1},
            "total_discount": {"$sum": "$discount_applied"},
            "total_revenue": {"$sum": "$total_amount"}
        }}
    ]
    order_stats = await db["orders"].aggregate(pipeline).to_list(1)
    
    stats = order_stats[0] if order_stats else {
        "total_usage": 0,
        "total_discount": 0,
        "total_revenue": 0
    }
    
    # Calculate averages
    avg_discount = stats["total_discount"] / stats["total_usage"] if stats["total_usage"] > 0 else 0
    
    # Top Coupon
    top_coupon = await db["coupons"].find().sort("usage_count", -1).limit(1).to_list(1)
    top_code = top_coupon[0]["code"] if top_coupon else "None"
    
    # Get total orders to calculate redemption rate
    total_orders = await db["orders"].count_documents({})
    redemption_rate = (stats["total_usage"] / total_orders * 100) if total_orders > 0 else 0

    return {
        "active_count": active_coupons,
        "expired_count": expired_coupons,
        "scheduled_count": scheduled_coupons,
        "total_usage": stats["total_usage"],
        "monthly_usage": int(stats["total_usage"] * 0.4), # Simulated
        "total_discount": stats["total_discount"],
        "total_revenue": stats["total_revenue"],
        "avg_discount": avg_discount,
        "redemption_rate": redemption_rate,
        "top_coupon": top_code
    }

# ---------------------------------------------------------
# AUTO-PROMOTIONS (Rules Engine)
# ---------------------------------------------------------

@router.get("/promotions/all")
async def list_promotions(current_admin: dict = Depends(get_current_admin)):
    """List all auto-apply promotions."""
    db = get_database()
    promotions = await db["promotions"].find().sort("created_at", -1).to_list(1000)
    for p in promotions:
        p["_id"] = str(p["_id"])
    return promotions

@router.post("/promotions")
async def create_promotion(data: dict, current_admin: dict = Depends(get_current_admin)):
    """Create a new auto-promotion rule."""
    db = get_database()
    
    promo_doc = {
        "id": str(uuid.uuid4()),
        "name": data.get("name"),
        "condition": data.get("condition"), # e.g. "order_amount > 1000"
        "action": data.get("action"), # e.g. {"type": "discount", "value": 10}
        "status": data.get("status", "Active"),
        "priority": int(data.get("priority", 0)),
        "created_at": datetime.now(timezone.utc)
    }
    
    await db["promotions"].insert_one(promo_doc)
    promo_doc["_id"] = str(promo_doc["_id"])
    return promo_doc
