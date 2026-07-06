from fastapi import APIRouter, Depends, HTTPException, status, Request, Query, WebSocket, WebSocketDisconnect
from typing import List, Any
import random
from app.models.order import OrderCreate, OrderResponse, OrderInDB, OrderBase
from app.core.security import get_current_user, get_current_admin
from app.core.db import get_database
from app.services.razorpay_service import create_order as razorpay_create_order, verify_payment_signature
from app.services.email_service import send_invoice_email
from datetime import datetime, timedelta
import uuid

router = APIRouter()

@router.post("/", response_model=OrderResponse)
async def create_order(order_in: OrderCreate, current_user: dict = Depends(get_current_user)):
    db = get_database()
    order_dict = order_in.model_dump()
    order_dict["_id"] = str(uuid.uuid4())
    order_dict["user_id"] = current_user["id"]
    order_dict.setdefault("payment_status", "Pending")
    order_dict.setdefault("order_status", "Pending")
    
    if order_in.payment_mode == "ONLINE":
        rz_order = razorpay_create_order(order_in.total_amount + 9)  # +9 packaging
        if not rz_order:
            raise HTTPException(status_code=500, detail="Could not create Razorpay order. Check RAZORPAY keys.")
        order_dict["razorpay_order_id"] = rz_order["id"]
    
    db_order = OrderInDB(**order_dict)
    await db["orders"].insert_one(db_order.model_dump(by_alias=True))
    return db_order

@router.get("/my-orders", response_model=List[OrderResponse])
async def read_my_orders(current_user: dict = Depends(get_current_user)):
    db = get_database()
    orders = await db["orders"].find({"user_id": current_user["id"]}).to_list(100)
    return orders

@router.get("/", response_model=List[OrderResponse], dependencies=[Depends(get_current_admin)])
async def read_all_orders(date: str = Query(None)):
    db = get_database()
    query = {}
    if date == "today":
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        query["created_at"] = {"$gte": today_start}
    orders = await db["orders"].find(query).sort("created_at", -1).to_list(100)
    return orders

@router.websocket("/{order_id}/ws")
async def order_tracking_ws(websocket: WebSocket, order_id: str):
    await websocket.accept()
    try:
        db = get_database()
        lat = 12.9716
        lng = 77.5946
        while True:
            # Simulate delivery partner moving
            lat += random.uniform(-0.001, 0.001)
            lng += random.uniform(-0.001, 0.001)
            
            order = await db["orders"].find_one({"_id": order_id})
            status_str = order.get("order_status", "Pending") if order else "Pending"

            await websocket.send_json({
                "order_id": order_id,
                "status": status_str,
                "location": {"lat": lat, "lng": lng},
                "estimated_time_mins": random.randint(5, 15) if status_str not in ["Delivered", "Cancelled"] else 0
            })
            import asyncio
            await asyncio.sleep(3)
    except WebSocketDisconnect:
        print(f"Client disconnected for order {order_id}")

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_by_id(order_id: str, current_user: dict = Depends(get_current_user)):
    db = get_database()
    order = await db["orders"].find_one({"_id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    # Verify the user owns the order or is an admin
    if order["user_id"] != current_user["id"] and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    return order

@router.post("/verify-payment")
async def verify_payment(request: Request):
    data = await request.json()
    razorpay_order_id = data.get("razorpay_order_id")
    razorpay_payment_id = data.get("razorpay_payment_id")
    razorpay_signature = data.get("razorpay_signature")
    order_id = data.get("order_id")
    
    if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
        raise HTTPException(status_code=400, detail="Missing Razorpay payment details")
    
    if verify_payment_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
        db = get_database()
        # Update by razorpay_order_id or order_id
        filter_q = {"_id": order_id} if order_id else {"razorpay_order_id": razorpay_order_id}
        await db["orders"].update_one(
            filter_q,
            {"$set": {"payment_status": "Completed", "razorpay_payment_id": razorpay_payment_id}}
        )
        return {"status": "success"}
    else:
        raise HTTPException(status_code=400, detail="Payment signature verification failed")

@router.put("/{order_id}/status", response_model=OrderResponse, dependencies=[Depends(get_current_admin)])
async def update_order_status(order_id: str, request: Request):
    data = await request.json()
    new_status = data.get("status")
    if not new_status:
        raise HTTPException(status_code=400, detail="Status is required")
        
    db = get_database()
    update_data = {"order_status": new_status}
    if new_status == "Cancelled":
        update_data["cancelled_by"] = "admin"
        
    updated = await db["orders"].find_one_and_update(
        {"_id": order_id},
        {"$set": update_data},
        return_document=True
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Order not found")
        
    if new_status == "Preparing":
        user = await db["users"].find_one({"_id": updated.get("user_id")})
        if user and user.get("email"):
            # Trigger email service asynchronously or non-blocking
            try:
                import asyncio
                asyncio.create_task(asyncio.to_thread(send_invoice_email, user.get("email"), updated))
            except Exception as e:
                print(f"Error sending email: {e}")

    return updated

@router.put("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(order_id: str, current_user: dict = Depends(get_current_user)):
    db = get_database()
    order = await db["orders"].find_one({"_id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    if order["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this order")
        
    if order.get("order_status") not in ["Pending", "Order Placed"]:
        raise HTTPException(status_code=400, detail="Order cannot be cancelled at this stage")
        
    # Check if within dynamic window
    settings = await db["settings"].find_one({"_id": "global_config"})
    cancel_window_mins = settings.get("cancel_window_mins", 5) if settings else 5

    created_at = order.get("created_at")
    if created_at:
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00")).replace(tzinfo=None)
        
        if datetime.utcnow() - created_at > timedelta(minutes=cancel_window_mins):
            raise HTTPException(status_code=400, detail=f"Cancellation window ({cancel_window_mins} minutes) has expired")

    updated = await db["orders"].find_one_and_update(
        {"_id": order_id},
        {"$set": {"order_status": "Cancelled", "cancelled_by": "user"}},
        return_document=True
    )
    return updated

@router.put("/{order_id}/assign", response_model=OrderResponse, dependencies=[Depends(get_current_admin)])
async def assign_delivery_partner(order_id: str, request: Request):
    data = await request.json()
    partner_id = data.get("delivery_partner_id")
    
    db = get_database()
    updated = await db["orders"].find_one_and_update(
        {"_id": order_id},
        {"$set": {"delivery_partner_id": partner_id}},
        return_document=True
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Order not found")
    return updated
