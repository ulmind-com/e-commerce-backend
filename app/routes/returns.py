from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, Any, List
from app.core.security import get_current_admin
from app.core.db import get_database
from datetime import datetime, timedelta
import uuid

router = APIRouter()

@router.get("/analytics", dependencies=[Depends(get_current_admin)])
async def get_returns_analytics() -> Dict[str, Any]:
    db = get_database()
    # Find all orders that have return-related statuses
    return_statuses = [
        "Return Requested", "Return Under Review", "Return Approved", "Return Rejected",
        "Refund Pending", "Refunded", "Replacement Sent", "Exchanged", "Cancelled"
    ]
    
    # Calculate mock analytics for now, but use real data where available
    pipeline = [
        {"$match": {"order_status": {"$in": return_statuses}}},
        {"$group": {
            "_id": "$order_status",
            "count": {"$sum": 1},
            "total_amount": {"$sum": "$total_amount"}
        }}
    ]
    
    try:
        results = await db["orders"].aggregate(pipeline).to_list(100)
    except AttributeError:
        # Fallback for in-memory DB during dev
        docs = await db["orders"].find({"order_status": {"$in": return_statuses}}).to_list(1000)
        results = []
        counts = {}
        amounts = {}
        for doc in docs:
            st = doc.get("order_status")
            counts[st] = counts.get(st, 0) + 1
            amounts[st] = amounts.get(st, 0) + doc.get("total_amount", 0)
        for st in counts:
            results.append({"_id": st, "count": counts[st], "total_amount": amounts[st]})

    stats = {
        "total_requests": 0,
        "pending": 0,
        "approved": 0,
        "rejected": 0,
        "refund_requests": 0,
        "refund_amount": 0,
        "exchange_requests": 0
    }
    
    for r in results:
        status = r.get("_id")
        count = r.get("count", 0)
        amount = r.get("total_amount", 0)
        stats["total_requests"] += count
        
        if status in ["Return Requested", "Return Under Review", "Cancelled"]:
            stats["pending"] += count
        elif status in ["Return Approved", "Refund Pending", "Refunded"]:
            stats["approved"] += count
            if status in ["Refund Pending", "Refunded"]:
                stats["refund_requests"] += count
            if status == "Refunded":
                stats["refund_amount"] += amount
        elif status == "Return Rejected":
            stats["rejected"] += count
        elif status in ["Exchanged", "Replacement Sent"]:
            stats["exchange_requests"] += count

    # Generate mock daily trend data (last 7 days)
    today = datetime.utcnow()
    daily_trend = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        daily_trend.append({
            "date": d.strftime("%Y-%m-%d"),
            "returns": 0, # Should be calculated from db
            "refunds": 0
        })

    # Return reasons mock
    reasons = [
        {"name": "Damaged Product", "value": 45},
        {"name": "Wrong Product", "value": 25},
        {"name": "Expired Product", "value": 15},
        {"name": "Missing Item", "value": 10},
        {"name": "Other", "value": 5}
    ]

    return {
        "kpis": stats,
        "daily_trend": daily_trend,
        "reasons": reasons,
        "return_rate": "5.2%",
        "avg_resolution_time": "24h 15m"
    }

@router.get("/", dependencies=[Depends(get_current_admin)])
async def get_all_returns(status: str = None, limit: int = 50, skip: int = 0) -> List[Dict[str, Any]]:
    db = get_database()
    return_statuses = [
        "Return Requested", "Return Under Review", "Return Approved", "Return Rejected",
        "Refund Pending", "Refunded", "Replacement Sent", "Exchanged", "Cancelled"
    ]
    
    query = {}
    if status and status != "All":
        query["order_status"] = status
    else:
        query["order_status"] = {"$in": return_statuses}
        
    orders = await db["orders"].find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    # We will map fields to look like an enterprise returns dashboard
    returns = []
    for order in orders:
        # Mock some return specific fields if they don't exist
        return_data = order.get("return_details", {})
        returns.append({
            "id": order.get("_id"),
            "order_id": order.get("_id"),
            "customer_id": order.get("user_id"),
            "total_amount": order.get("total_amount"),
            "payment_mode": order.get("payment_mode"),
            "status": order.get("order_status"),
            "reason": return_data.get("reason", "Not Specified"),
            "requested_date": return_data.get("requested_at", order.get("created_at")),
            "items": order.get("items", []),
            "customer_notes": return_data.get("customer_notes", ""),
            "admin_notes": return_data.get("admin_notes", ""),
            "images": return_data.get("images", []),
            "inspection_status": return_data.get("inspection_status", "Pending")
        })
        
    return returns

@router.put("/{order_id}/status", dependencies=[Depends(get_current_admin)])
async def update_return_status(order_id: str, request: Request) -> Dict[str, Any]:
    data = await request.json()
    new_status = data.get("status")
    admin_notes = data.get("admin_notes", "")
    
    if not new_status:
        raise HTTPException(status_code=400, detail="Status is required")

    db = get_database()
    
    update_doc = {
        "order_status": new_status,
        "return_details.admin_notes": admin_notes,
        "return_details.updated_at": datetime.utcnow()
    }
    
    result = await db["orders"].update_one(
        {"_id": order_id},
        {"$set": update_doc}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
        
    # TODO: Trigger Notifications, Razorpay Refund, Inventory Update based on new_status
    
    return {"status": "success", "message": f"Status updated to {new_status}"}

@router.post("/{order_id}/inspection", dependencies=[Depends(get_current_admin)])
async def submit_inspection(order_id: str, request: Request) -> Dict[str, Any]:
    data = await request.json()
    result = data.get("result") # "Pass" or "Fail"
    restock = data.get("restock", False)
    notes = data.get("notes", "")
    
    db = get_database()
    order = await db["orders"].find_one({"_id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    update_doc = {
        "return_details.inspection_status": result,
        "return_details.inspection_notes": notes,
        "return_details.inspected_at": datetime.utcnow(),
        "order_status": "Return Approved" if result == "Pass" else "Return Rejected"
    }
    
    await db["orders"].update_one(
        {"_id": order_id},
        {"$set": update_doc}
    )
    
    if result == "Pass" and restock:
        # Update inventory
        for item in order.get("items", []):
            product_id = item.get("product_id")
            qty = item.get("quantity", 1)
            await db["products"].update_one(
                {"_id": product_id},
                {"$inc": {"stock_quantity": qty}}
            )
            
    return {"status": "success", "message": "Inspection submitted"}

@router.post("/{order_id}/refund/manual", dependencies=[Depends(get_current_admin)])
async def process_manual_refund(order_id: str, request: Request) -> Dict[str, Any]:
    data = await request.json()
    method = data.get("method") # UPI, Bank Transfer, Store Credit
    transaction_id = data.get("transaction_id")
    amount = data.get("amount")
    
    db = get_database()
    update_doc = {
        "order_status": "Refunded",
        "payment_status": "Refunded",
        "return_details.refund_method": method,
        "return_details.refund_transaction_id": transaction_id,
        "return_details.refunded_amount": amount,
        "return_details.refunded_at": datetime.utcnow()
    }
    
    result = await db["orders"].update_one(
        {"_id": order_id},
        {"$set": update_doc}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
        
    return {"status": "success", "message": "Manual refund processed successfully"}
