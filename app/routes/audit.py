from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from bson import ObjectId
from app.core.security import get_current_admin
from app.core.db import get_database
from datetime import datetime, timedelta
import random

router = APIRouter()

# ──────────────────────────────────────────────────────────
# HELPER: INSERT AUDIT LOG
# ──────────────────────────────────────────────────────────
async def insert_audit_log(
    user_id: str,
    user_name: str,
    role: str,
    module: str,
    action: str,
    status: str = "Success",
    severity: str = "Info",
    ip_address: str = "127.0.0.1",
    device: str = "Unknown",
    location: str = "Unknown",
    metadata: dict = None
):
    db = get_database()
    log_entry = {
        "timestamp": datetime.utcnow(),
        "user_id": user_id,
        "user_name": user_name,
        "role": role,
        "module": module,
        "action": action,
        "status": status,
        "severity": severity,
        "ip_address": ip_address,
        "device": device,
        "location": location,
        "metadata": metadata or {}
    }
    await db["audit_logs"].insert_one(log_entry)

# ──────────────────────────────────────────────────────────
# SEEDING: GENERATE MOCK LOGS IF EMPTY
# ──────────────────────────────────────────────────────────
async def seed_audit_logs_if_empty():
    db = get_database()
    count = await db["audit_logs"].count_documents({})
    if count > 0:
        return
        
    modules = ["Authentication", "Orders", "Products", "Finance", "Inventory", "Staff", "Suppliers", "Security"]
    actions = {
        "Authentication": ["Login", "Logout", "Failed Login", "Password Reset"],
        "Orders": ["Order Created", "Order Cancelled", "Order Shipped", "Refund Issued"],
        "Products": ["Product Added", "Price Changed", "Stock Updated"],
        "Finance": ["Payment Received", "Invoice Generated", "Settlement Done"],
        "Inventory": ["Stock In", "Stock Out", "Warehouse Transfer"],
        "Security": ["Permission Changed", "2FA Enabled", "API Key Generated"]
    }
    severities = ["Info", "Warning", "High", "Critical"]
    statuses = ["Success", "Failed", "Pending"]
    users = [
        {"name": "Admin User", "role": "Super Admin"},
        {"name": "Finance Head", "role": "Finance Manager"},
        {"name": "System Agent", "role": "System"},
        {"name": "Warehouse Mgr", "role": "Inventory Manager"}
    ]
    devices = ["MacBook Pro (macOS)", "Windows 11 PC", "iPhone 14 Pro", "Ubuntu Server"]
    locations = ["Mumbai, India", "Delhi, India", "Bengaluru, India", "Unknown"]
    
    logs = []
    now = datetime.utcnow()
    
    for i in range(150):
        mod = random.choice(modules)
        act = random.choice(actions.get(mod, ["Data Updated"]))
        u = random.choice(users)
        sev = "Info"
        stat = "Success"
        
        if "Failed" in act or act == "Order Cancelled":
            sev = "Warning"
            stat = "Failed"
            
        if "Permission" in act or "API Key" in act:
            sev = random.choice(["High", "Critical"])
            
        timestamp = now - timedelta(hours=random.randint(0, 168), minutes=random.randint(0, 59))
        
        logs.append({
            "timestamp": timestamp,
            "user_id": str(ObjectId()),
            "user_name": u["name"],
            "role": u["role"],
            "module": mod,
            "action": act,
            "status": stat,
            "severity": sev,
            "ip_address": f"{random.randint(10, 255)}.{random.randint(10, 255)}.{random.randint(10, 255)}.{random.randint(10, 255)}",
            "device": random.choice(devices),
            "location": random.choice(locations),
            "metadata": {"details": f"Generated simulated event for {act}", "event_id": f"EVT-{random.randint(1000,9999)}"}
        })
        
    await db["audit_logs"].insert_many(logs)

# ──────────────────────────────────────────────────────────
# DASHBOARD
# ──────────────────────────────────────────────────────────
@router.get("/dashboard")
async def get_audit_dashboard(current_admin: dict = Depends(get_current_admin)):
    await seed_audit_logs_if_empty()
    db = get_database()
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)
    
    today_activities = await db["audit_logs"].count_documents({"timestamp": {"$gte": yesterday}})
    failed_logins = await db["audit_logs"].count_documents({"action": "Failed Login", "timestamp": {"$gte": yesterday}})
    security_alerts = await db["audit_logs"].count_documents({"severity": {"$in": ["High", "Critical"]}, "timestamp": {"$gte": yesterday}})
    active_sessions = random.randint(12, 45) # Mocked active sessions for demo
    
    # Generate heatmap data (last 7 days activity count)
    heatmap = []
    for i in range(7):
        date_start = now - timedelta(days=i+1)
        date_end = now - timedelta(days=i)
        count = await db["audit_logs"].count_documents({"timestamp": {"$gte": date_start, "$lt": date_end}})
        heatmap.append({"date": date_start.strftime("%Y-%m-%d"), "events": count})
    heatmap.reverse()
    
    return {
        "kpis": {
            "today_activities": today_activities,
            "active_sessions": active_sessions,
            "failed_logins": failed_logins,
            "security_alerts": security_alerts,
            "critical_events": await db["audit_logs"].count_documents({"severity": "Critical"}),
            "permission_changes": await db["audit_logs"].count_documents({"action": {"$regex": "Permission"}}),
            "orders_modified": await db["audit_logs"].count_documents({"module": "Orders", "action": {"$regex": "Updated"}}),
            "products_updated": await db["audit_logs"].count_documents({"module": "Products"}),
            "payments_processed": await db["audit_logs"].count_documents({"module": "Finance", "action": "Payment Received"})
        },
        "heatmap": heatmap
    }

# ──────────────────────────────────────────────────────────
# GET ALL LOGS (WITH FILTERING)
# ──────────────────────────────────────────────────────────
@router.get("/logs")
async def get_audit_logs(
    module: Optional[str] = None,
    severity: Optional[str] = None,
    user_name: Optional[str] = None,
    limit: int = 100,
    current_admin: dict = Depends(get_current_admin)
):
    await seed_audit_logs_if_empty()
    db = get_database()
    
    query = {}
    if module and module != "All":
        query["module"] = module
    if severity and severity != "All":
        query["severity"] = severity
    if user_name:
        query["user_name"] = {"$regex": user_name, "$options": "i"}
        
    cursor = db["audit_logs"].find(query).sort("timestamp", -1).limit(limit)
    logs = await cursor.to_list(limit)
    
    for log in logs:
        log["id"] = str(log["_id"])
        del log["_id"]
        # format timestamp
        log["time_str"] = log["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        
    return logs

# ──────────────────────────────────────────────────────────
# ALERTS
# ──────────────────────────────────────────────────────────
@router.get("/alerts")
async def get_security_alerts(current_admin: dict = Depends(get_current_admin)):
    await seed_audit_logs_if_empty()
    db = get_database()
    
    cursor = db["audit_logs"].find({"severity": {"$in": ["High", "Critical"]}}).sort("timestamp", -1).limit(20)
    alerts = await cursor.to_list(20)
    
    for a in alerts:
        a["id"] = str(a["_id"])
        del a["_id"]
        a["time_str"] = a["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        
    return alerts
