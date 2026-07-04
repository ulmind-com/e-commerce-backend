from fastapi import APIRouter, Depends, HTTPException
from typing import List, Any
from app.core.security import get_current_admin
from app.core.db import get_database
from app.models.user import UserResponse
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_metrics(current_admin: dict = Depends(get_current_admin)):
    db = get_database()
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Orders today
    orders_today = await db["orders"].count_documents({"created_at": {"$gte": today_start}})
    
    # Revenue today
    pipeline = [
        {"$match": {"created_at": {"$gte": today_start}}},
        {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
    ]
    rev_res = await db["orders"].aggregate(pipeline).to_list(1)
    revenue_today = rev_res[0]["total"] if rev_res else 0.0
    
    # Low stock items (less than 10 units)
    low_stock_count = await db["products"].count_documents({"stock_quantity": {"$lt": 10}})
    
    # Active delivery partners
    partners_count = await db["users"].count_documents({"role": "delivery_partner"})
    
    # Recent orders (last 10)
    recent_orders = await db["orders"].find().sort("created_at", -1).limit(10).to_list(10)
    
    return {
        "orders_today": orders_today,
        "revenue_today": revenue_today,
        "low_stock_count": low_stock_count,
        "active_delivery_partners": partners_count,
        "recent_orders": recent_orders
    }

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(current_admin: dict = Depends(get_current_admin)):
    db = get_database()
    users = await db["users"].find().to_list(500)
    for user in users:
        user["_id"] = str(user["_id"])
    return users

@router.get("/delivery-partners", response_model=List[UserResponse])
async def get_delivery_partners(current_admin: dict = Depends(get_current_admin)):
    db = get_database()
    partners = await db["users"].find({"role": "delivery_partner"}).to_list(100)
    for partner in partners:
        partner["_id"] = str(partner["_id"])
    return partners
