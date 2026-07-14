from fastapi import APIRouter, Depends, Request, HTTPException
from typing import Dict, Any
from app.core.security import get_current_admin
from app.core.db import get_database

router = APIRouter()

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
    
    # Extract fields with defaults
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
