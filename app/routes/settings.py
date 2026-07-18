from fastapi import APIRouter, Depends, Request, HTTPException, Body
from typing import Dict, Any
from app.core.security import get_current_admin
from app.core.db import get_database
from datetime import datetime

router = APIRouter()

# ──────────────────────────────────────────────────────────
# ENTERPRISE GLOBAL SETTINGS
# ──────────────────────────────────────────────────────────

DEFAULT_SETTINGS = {
    "store": {
        "name": "OneBasket Enterprise",
        "email": "support@onebasket.com",
        "phone": "+91-9876543210",
        "address": "123 Business Avenue, Tech Park",
        "currency": "INR (₹)",
        "timezone": "Asia/Kolkata",
        "gst_number": "22AAAAA0000A1Z5"
    },
    "orders": {
        "auto_confirm": True,
        "auto_cancel_hours": 24,
        "min_order_value": 100,
        "max_order_value": 50000
    },
    "delivery": {
        "radius_km": 15,
        "base_charge": 40,
        "free_delivery_threshold": 500,
        "express_enabled": True
    },
    "payments": {
        "razorpay_enabled": True,
        "cod_enabled": True,
        "upi_enabled": True,
        "cod_max_limit": 5000
    },
    "ai": {
        "enabled": True,
        "provider": "Antigravity Statistical Engine",
        "auto_pricing": False,
        "auto_reorder": True
    },
    "legal": {
        "privacy_policy": "",
        "terms": "",
        "refund_policy": ""
    },
    "seo": {
        "meta_title": "OneBasket | Premium Groceries",
        "meta_description": "Order fresh groceries online."
    }
}

@router.get("/all")
async def get_all_settings(current_admin: dict = Depends(get_current_admin)) -> Dict[str, Any]:
    db = get_database()
    settings = await db["settings"].find_one({"_id": "global_enterprise_settings"})
    
    if not settings:
        return DEFAULT_SETTINGS
        
    settings.pop("_id", None)
    
    # Merge with defaults in case of new fields
    result = DEFAULT_SETTINGS.copy()
    for category, values in settings.items():
        if category in result and isinstance(values, dict):
            result[category].update(values)
        else:
            result[category] = values
            
    return result

@router.put("/update", dependencies=[Depends(get_current_admin)])
async def update_all_settings(payload: Dict[str, Any] = Body(...), current_admin: dict = Depends(get_current_admin)) -> Dict[str, Any]:
    db = get_database()
    
    # Update settings
    await db["settings"].update_one(
        {"_id": "global_enterprise_settings"},
        {"$set": payload},
        upsert=True
    )
    
    # Attempt to log to Audit
    try:
        log_entry = {
            "timestamp": datetime.utcnow(),
            "user_id": str(current_admin.get("_id", "system")),
            "user_name": current_admin.get("email", "Admin"),
            "role": "Super Admin",
            "module": "Settings",
            "action": "Global Configuration Updated",
            "status": "Success",
            "severity": "Warning",
            "ip_address": "127.0.0.1",
            "device": "Web Dashboard",
            "location": "System",
            "metadata": {"updated_categories": list(payload.keys())}
        }
        await db["audit_logs"].insert_one(log_entry)
    except Exception:
        pass # Ignore audit failure so it doesn't break settings save
        
    return {"status": "success", "message": "Settings updated globally."}

# ──────────────────────────────────────────────────────────
# LEGACY ROUTES (Preserved to avoid breaking existing modules)
# ──────────────────────────────────────────────────────────

@router.get("/")
async def get_settings() -> Dict[str, Any]:
    db = get_database()
    settings = await db["settings"].find_one({"_id": "global_config"})
    if not settings:
        return {"cancel_window_mins": 5}
    return {"cancel_window_mins": settings.get("cancel_window_mins", 5)}

@router.put("/cancel-window", dependencies=[Depends(get_current_admin)])
async def update_cancel_window(request: Request) -> Dict[str, Any]:
    data = await request.json()
    minutes = data.get("minutes")
    if not isinstance(minutes, (int, float)) or minutes < 0:
        raise HTTPException(status_code=400, detail="Invalid minutes provided")

    db = get_database()
    await db["settings"].update_one(
        {"_id": "global_config"},
        {"$set": {"cancel_window_mins": minutes}},
        upsert=True
    )
    return {"status": "success", "cancel_window_mins": minutes}

@router.get("/shop-location")
async def get_shop_location() -> Dict[str, Any]:
    db = get_database()
    settings = await db["settings"].find_one({"_id": "shop_location"})
    if not settings:
        return {"lat": 28.6139, "lng": 77.2090, "express_delivery_max_distance": 5.0}
    return {
        "lat": settings.get("lat"), 
        "lng": settings.get("lng"),
        "express_delivery_max_distance": settings.get("express_delivery_max_distance", 5.0)
    }

@router.put("/shop-location", dependencies=[Depends(get_current_admin)])
async def update_shop_location(request: Request) -> Dict[str, Any]:
    data = await request.json()
    lat = data.get("lat")
    lng = data.get("lng")
    max_distance = data.get("express_delivery_max_distance", 5.0)
    
    if lat is None or lng is None:
        raise HTTPException(status_code=400, detail="Invalid coordinates provided")

    db = get_database()
    await db["settings"].update_one(
        {"_id": "shop_location"},
        {"$set": {
            "lat": float(lat), 
            "lng": float(lng),
            "express_delivery_max_distance": float(max_distance)
        }},
        upsert=True
    )
    return {"status": "success", "lat": lat, "lng": lng, "express_delivery_max_distance": max_distance}

@router.get("/payments")
async def get_payment_settings() -> Dict[str, Any]:
    db = get_database()
    settings = await db["settings"].find_one({"_id": "payment_config"})
    if not settings:
        return {
            "cod_enabled": True,
            "cod_start_time": "09:00",
            "cod_end_time": "22:30",
            "cod_min_order": 200,
            "cod_max_order": 5000,
            "cod_surcharge": 0
        }
    settings.pop("_id", None)
    return settings

@router.put("/payments", dependencies=[Depends(get_current_admin)])
async def update_payment_settings(request: Request) -> Dict[str, Any]:
    data = await request.json()
    
    update_data = {
        "cod_enabled": data.get("cod_enabled", True),
        "cod_start_time": data.get("cod_start_time", "09:00"),
        "cod_end_time": data.get("cod_end_time", "22:30"),
        "cod_min_order": float(data.get("cod_min_order", 200)),
        "cod_max_order": float(data.get("cod_max_order", 5000)),
        "cod_surcharge": float(data.get("cod_surcharge", 0))
    }

    db = get_database()
    await db["settings"].update_one(
        {"_id": "payment_config"},
        {"$set": update_data},
        upsert=True
    )
    return {"status": "success", "settings": update_data}
