from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, Any, List
from app.core.security import get_current_admin
from app.core.db import get_database
from datetime import datetime, timedelta

router = APIRouter()

DEFAULT_COD_CONFIG = {
    "status": "enabled",  # enabled, disabled, maintenance, emergency
    "business_hours": {
        "store_open": "08:00",
        "store_close": "22:00",
        "cod_start": "09:00",
        "cod_end": "21:30",
    },
    "automation_rules": {
        "disable_on_store_closed": True,
        "disable_on_low_inventory": False,
        "disable_in_weather_emergency": False,
        "pause_on_peak_orders": False,
        "disable_on_holidays": True,
    },
    "zones": [
        {"id": "z1", "name": "Core City Zone", "radius": 5, "charge": 0, "min_order": 100, "max_order": 2000, "max_cod_orders": 100, "eta": "15-30 mins", "active": True},
        {"id": "z2", "name": "Suburban Ring", "radius": 15, "charge": 20, "min_order": 200, "max_order": 1500, "max_cod_orders": 50, "eta": "45-60 mins", "active": True},
    ],
    "pincodes": {
        "allowed": ["700001", "700002", "700003"],
        "blocked": ["700099"],
        "premium": ["700020"],
    },
    "product_rules": {
        "disabled_categories": ["Electronics", "Jewelry"],
        "disabled_brands": ["Apple", "Samsung"],
        "disabled_price_range": {"min": 5000, "max": 999999},
    },
    "order_value_rules": {
        "min_amount": 100,
        "max_amount": 5000,
        "base_charge": 0,
        "free_cod_above": 500,
    },
    "customer_rules": {
        "new_customer_limit": 1000,
        "max_orders_per_customer": 3,
        "high_return_threshold_percent": 30,
        "block_fraudulent": True,
    },
    "schedules": {
        "holidays": ["2026-08-15", "2026-10-02"],
        "active_schedule": "default"
    }
}

@router.get("/config")
async def get_cod_config() -> Dict[str, Any]:
    db = get_database()
    config = await db["settings"].find_one({"_id": "cod_master_config"})
    if not config:
        return DEFAULT_COD_CONFIG
    config.pop("_id", None)
    return config

@router.put("/config", dependencies=[Depends(get_current_admin)])
async def update_cod_config(request: Request) -> Dict[str, Any]:
    data = await request.json()
    db = get_database()
    await db["settings"].update_one(
        {"_id": "cod_master_config"},
        {"$set": data},
        upsert=True
    )
    return {"status": "success", "message": "COD Configuration updated successfully"}

@router.get("/analytics")
async def get_cod_analytics(dependencies=[Depends(get_current_admin)]) -> Dict[str, Any]:
    db = get_database()
    
    # Calculate today's dates
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = today_start.replace(day=1)

    # 1. Pipeline for COD Orders (Today)
    today_cod_orders = await db["orders"].find({
        "payment_mode": "COD",
        "created_at": {"$gte": today_start}
    }).to_list(1000)

    today_revenue = sum([o.get("total_amount", 0) for o in today_cod_orders if o.get("order_status") in ["Delivered", "Completed"]])
    pending_orders = len([o for o in today_cod_orders if o.get("order_status") in ["Pending", "Order Placed", "Preparing", "Out for Delivery"]])
    delivered_orders = len([o for o in today_cod_orders if o.get("order_status") in ["Delivered", "Completed"]])
    cancelled_orders = len([o for o in today_cod_orders if o.get("order_status") == "Cancelled"])
    failed_orders = len([o for o in today_cod_orders if o.get("order_status") == "Failed"])

    total_today = len(today_cod_orders)
    success_rate = (delivered_orders / total_today * 100) if total_today > 0 else 0
    return_rate = (cancelled_orders / total_today * 100) if total_today > 0 else 0

    # 2. Pipeline for Monthly Revenue
    monthly_cod_orders = await db["orders"].find({
        "payment_mode": "COD",
        "created_at": {"$gte": month_start},
        "order_status": {"$in": ["Delivered", "Completed"]}
    }).to_list(10000)
    
    monthly_revenue = sum([o.get("total_amount", 0) for o in monthly_cod_orders])
    
    # 3. Collection Pending (Delivered but cash not deposited - using dummy data for un-integrated parts)
    # We assume 'payment_status' == 'Pending' means cash not yet verified by finance
    collection_pending = sum([o.get("total_amount", 0) for o in today_cod_orders if o.get("order_status") == "Delivered" and o.get("payment_status") != "Completed"])

    avg_order_value = (today_revenue / delivered_orders) if delivered_orders > 0 else 0

    return {
        "status": "active",
        "today_orders": total_today,
        "today_revenue": today_revenue,
        "pending_orders": pending_orders,
        "delivered_orders": delivered_orders,
        "cancelled_orders": cancelled_orders,
        "failed_orders": failed_orders,
        "success_rate": round(success_rate, 1),
        "return_rate": round(return_rate, 1),
        "collection_pending": collection_pending,
        "monthly_revenue": monthly_revenue,
        "avg_order_value": round(avg_order_value, 2),
        "ai_risk_score": 12, # mock risk score
    }

@router.get("/collections")
async def get_cod_collections(dependencies=[Depends(get_current_admin)]) -> List[Dict[str, Any]]:
    # Mock data for live operations collection view
    return [
        {"agent": "Ramesh P", "zone": "Core City", "collected": 4500, "pending": 1200, "status": "On Route"},
        {"agent": "Suresh K", "zone": "Suburban", "collected": 8900, "pending": 0, "status": "Deposited"},
        {"agent": "Vikram D", "zone": "South Hub", "collected": 2300, "pending": 500, "status": "On Route"}
    ]
