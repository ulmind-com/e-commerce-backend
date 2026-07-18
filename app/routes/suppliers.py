from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Dict, Any
from bson import ObjectId
from app.core.security import get_current_admin
from app.core.db import get_database
from datetime import datetime, timedelta
import random

router = APIRouter()

# ──────────────────────────────────────────────────────────
# DASHBOARD
# ──────────────────────────────────────────────────────────
@router.get("/dashboard")
async def get_srm_dashboard(current_admin: dict = Depends(get_current_admin)):
    db = get_database()
    now = datetime.utcnow()
    
    total_suppliers = await db["srm_suppliers"].count_documents({})
    active_suppliers = await db["srm_suppliers"].count_documents({"status": "Active"})
    
    total_pos = await db["srm_pos"].count_documents({})
    pending_deliveries = await db["srm_pos"].count_documents({"status": "Sent"})
    
    # Calculate outstanding balance
    payments_cursor = db["srm_payments"].find({})
    payments = await payments_cursor.to_list(1000)
    outstanding_balance = sum(p.get("amount", 0) for p in payments if p.get("status") == "Pending")

    return {
        "kpis": {
            "total_suppliers": total_suppliers,
            "active_suppliers": active_suppliers,
            "inactive_suppliers": total_suppliers - active_suppliers,
            "preferred_suppliers": await db["srm_suppliers"].count_documents({"category": "Preferred"}),
            "pending_approvals": await db["srm_pos"].count_documents({"status": "Pending"}),
            "total_pos": total_pos,
            "pending_deliveries": pending_deliveries,
            "completed_deliveries": await db["srm_pos"].count_documents({"status": "Received"}),
            "pending_payments": len([p for p in payments if p.get("status") == "Pending"]),
            "supplier_rating": 4.5,
            "inventory_value": 0, # Should ideally be calculated from products
            "outstanding_balance": outstanding_balance
        },
        "purchase_trend": [
            {"date": (now - timedelta(days=i)).strftime("%a"), "amount": random.randint(5000, 20000)} 
            for i in range(6, -1, -1)
        ],
        "ai_insights": [
            {"type": "positive", "text": "Average supplier lead time has decreased by 12% this month."},
            {"type": "warning", "text": "Supplier 'FreshFarms' has a 15% defect rate. Consider alternative sourcing."},
            {"type": "neutral", "text": "Optimal reorder point for 'Dairy' category reached."}
        ]
    }

# ──────────────────────────────────────────────────────────
# DIRECTORY
# ──────────────────────────────────────────────────────────
@router.get("/directory")
async def get_suppliers(current_admin: dict = Depends(get_current_admin)):
    db = get_database()
    suppliers = await db["srm_suppliers"].find().sort("created_at", -1).to_list(1000)
    for s in suppliers:
        s["id"] = str(s["_id"])
        del s["_id"]
    return suppliers

@router.post("/directory")
async def add_supplier(payload: dict = Body(...), current_admin: dict = Depends(get_current_admin)):
    db = get_database()
    
    # Check if GST exists
    existing = await db["srm_suppliers"].find_one({"gst_number": payload.get("gst_number")})
    if existing and payload.get("gst_number"):
        raise HTTPException(status_code=400, detail="Supplier with this GST already exists")
        
    entry = {
        "company_name": payload.get("company_name"),
        "owner_name": payload.get("owner_name"),
        "email": payload.get("email"),
        "phone": payload.get("phone"),
        "gst_number": payload.get("gst_number", ""),
        "category": payload.get("category", "General"),
        "status": "Active",
        "address": payload.get("address", ""),
        "created_at": datetime.utcnow()
    }
    
    result = await db["srm_suppliers"].insert_one(entry)
    
    # add supplier_id
    supplier_id = f"SUP-{str(result.inserted_id)[-6:].upper()}"
    await db["srm_suppliers"].update_one({"_id": result.inserted_id}, {"$set": {"supplier_id": supplier_id}})
    
    return {"message": "Supplier added successfully", "id": str(result.inserted_id)}

# ──────────────────────────────────────────────────────────
# PURCHASE ORDERS (POs)
# ──────────────────────────────────────────────────────────
@router.get("/pos")
async def get_pos(current_admin: dict = Depends(get_current_admin)):
    db = get_database()
    pos = await db["srm_pos"].find().sort("created_at", -1).to_list(1000)
    for p in pos:
        p["id"] = str(p["_id"])
        del p["_id"]
    return pos

@router.post("/pos")
async def create_po(payload: dict = Body(...), current_admin: dict = Depends(get_current_admin)):
    db = get_database()
    
    supplier = await db["srm_suppliers"].find_one({"_id": ObjectId(payload.get("supplier_id"))})
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
        
    entry = {
        "supplier_id": payload.get("supplier_id"),
        "supplier_name": supplier.get("company_name"),
        "products": payload.get("products", "Assorted Goods"),
        "quantity": payload.get("quantity", 0),
        "total_cost": payload.get("total_cost", 0),
        "status": "Pending", # Pending -> Sent -> Received
        "expected_date": payload.get("expected_date", (datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d")),
        "created_at": datetime.utcnow()
    }
    
    result = await db["srm_pos"].insert_one(entry)
    
    po_number = f"PO-{str(result.inserted_id)[-6:].upper()}"
    await db["srm_pos"].update_one({"_id": result.inserted_id}, {"$set": {"po_number": po_number}})
    
    return {"message": "Purchase Order created successfully"}

@router.put("/pos/{id}/status")
async def update_po_status(id: str, payload: dict = Body(...), current_admin: dict = Depends(get_current_admin)):
    db = get_database()
    status = payload.get("status")
    result = await db["srm_pos"].update_one({"_id": ObjectId(id)}, {"$set": {"status": status}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="PO not found")
    
    if status == "Sent":
        # Simulate sending PO and creating a pending payment
        po = await db["srm_pos"].find_one({"_id": ObjectId(id)})
        payment = {
            "po_id": str(po["_id"]),
            "po_number": po["po_number"],
            "supplier_id": po["supplier_id"],
            "supplier_name": po["supplier_name"],
            "amount": po["total_cost"],
            "status": "Pending",
            "due_date": (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "created_at": datetime.utcnow()
        }
        await db["srm_payments"].insert_one(payment)

    return {"message": f"PO status updated to {status}"}

# ──────────────────────────────────────────────────────────
# GOODS RECEIPT (GRN)
# ──────────────────────────────────────────────────────────
@router.get("/grn")
async def get_grns(current_admin: dict = Depends(get_current_admin)):
    db = get_database()
    grns = await db["srm_grn"].find().sort("created_at", -1).to_list(1000)
    for g in grns:
        g["id"] = str(g["_id"])
        del g["_id"]
    return grns

@router.post("/grn")
async def receive_goods(payload: dict = Body(...), current_admin: dict = Depends(get_current_admin)):
    db = get_database()
    po_id = payload.get("po_id")
    po = await db["srm_pos"].find_one({"_id": ObjectId(po_id)})
    if not po:
        raise HTTPException(status_code=404, detail="PO not found")
        
    received = int(payload.get("received_quantity", 0))
    damaged = int(payload.get("damaged_quantity", 0))
    accepted = received - damaged
    
    entry = {
        "po_id": po_id,
        "po_number": po.get("po_number"),
        "supplier_name": po.get("supplier_name"),
        "received_quantity": received,
        "damaged_quantity": damaged,
        "accepted_quantity": accepted,
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "created_at": datetime.utcnow()
    }
    
    result = await db["srm_grn"].insert_one(entry)
    
    grn_number = f"GRN-{str(result.inserted_id)[-6:].upper()}"
    await db["srm_grn"].update_one({"_id": result.inserted_id}, {"$set": {"grn_number": grn_number}})
    
    # Mark PO as Received
    await db["srm_pos"].update_one({"_id": ObjectId(po_id)}, {"$set": {"status": "Received"}})
    
    return {"message": "Goods received successfully"}

# ──────────────────────────────────────────────────────────
# PAYMENTS & FINANCE
# ──────────────────────────────────────────────────────────
@router.get("/payments")
async def get_payments(current_admin: dict = Depends(get_current_admin)):
    db = get_database()
    payments = await db["srm_payments"].find().sort("created_at", -1).to_list(1000)
    for p in payments:
        p["id"] = str(p["_id"])
        del p["_id"]
    return payments

@router.post("/payments/{id}/pay")
async def make_payment(id: str, payload: dict = Body(...), current_admin: dict = Depends(get_current_admin)):
    db = get_database()
    payment = await db["srm_payments"].find_one({"_id": ObjectId(id)})
    if not payment:
        raise HTTPException(status_code=404, detail="Payment record not found")
        
    if payment.get("status") == "Paid":
        raise HTTPException(status_code=400, detail="Payment already completed")
        
    result = await db["srm_payments"].update_one(
        {"_id": ObjectId(id)}, 
        {"$set": {
            "status": "Paid", 
            "payment_mode": payload.get("mode", "Bank Transfer"),
            "transaction_id": payload.get("transaction_id", f"TXN-{random.randint(10000, 99999)}")
        }}
    )
    return {"message": "Payment processed successfully"}
