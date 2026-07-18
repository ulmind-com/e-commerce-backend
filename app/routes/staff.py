from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Dict, Any
from bson import ObjectId
from app.core.security import get_current_admin, get_password_hash
from app.core.db import get_database
from datetime import datetime, timedelta
import random

router = APIRouter()

# ──────────────────────────────────────────────────────────
# DASHBOARD
# ──────────────────────────────────────────────────────────
@router.get("/dashboard")
async def get_staff_dashboard(current_admin: dict = Depends(get_current_admin)):
    db = get_database()
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    staff_cursor = db["users"].find({"role": {"$ne": "customer"}})
    staff = await staff_cursor.to_list(1000)
    total_staff = len(staff)
    
    # Calculate live metrics
    today_str = now.strftime("%Y-%m-%d")
    
    # Leaves today
    leaves_today = await db["hrms_leaves"].count_documents({
        "status": "Approved", 
        "from": {"$lte": today_str}, 
        "to": {"$gte": today_str}
    })
    
    # Present today (clocked in)
    present_today = await db["hrms_attendance"].count_documents({
        "date": today_str
    })
    
    late_arrivals = await db["hrms_attendance"].count_documents({
        "date": today_str,
        "status": "Late"
    })
    
    pending_leaves = await db["hrms_leaves"].count_documents({"status": "Pending"})

    return {
        "kpis": {
            "total_staff": total_staff,
            "active_staff": total_staff,
            "inactive_staff": 0,
            "on_leave": leaves_today,
            "present_today": present_today,
            "absent_today": max(0, total_staff - present_today - leaves_today),
            "late_arrivals": late_arrivals,
            "new_employees": 1,
            "resigned_employees": 0,
            "pending_approvals": pending_leaves,
            "total_departments": 7,
            "avg_performance": 4.2
        },
        "attendance_trend": [
            {"date": (today_start - timedelta(days=i)).strftime("%a"), "present": max(0, total_staff - random.randint(0, 3)), "absent": random.randint(0, 3)} 
            for i in range(6, -1, -1)
        ],
        "ai_insights": [
            {"type": "positive", "text": "Productivity is up by 15% this week in the Operations department."},
            {"type": "warning", "text": "High leave rate predicted for next week due to upcoming holidays. Plan warehouse shifts accordingly."},
            {"type": "neutral", "text": "Average performance score has remained steady at 4.2 for the past 3 quarters."}
        ]
    }

# ──────────────────────────────────────────────────────────
# DIRECTORY
# ──────────────────────────────────────────────────────────
@router.get("/directory")
async def get_staff_directory(current_admin: dict = Depends(get_current_admin)):
    db = get_database()
    staff = await db["users"].find({"role": {"$ne": "customer"}}).to_list(1000)
    
    directory = []
    for idx, member in enumerate(staff):
        member_id = str(member.get("_id"))
        directory.append({
            "id": member_id,
            "employee_id": member.get("employee_id", f"EMP-{member_id[-6:].upper()}"),
            "name": member.get("full_name", "Unknown"),
            "email": member.get("email"),
            "phone": member.get("phone", "+91-0000000000"),
            "role": member.get("role", "admin").capitalize(),
            "department": member.get("department", "Operations"),
            "designation": member.get("designation", "Staff"),
            "status": member.get("status", "Active"),
            "joining_date": member.get("created_at", datetime.utcnow()).strftime("%Y-%m-%d"),
            "salary": member.get("salary", 45000),
            "avatar": member.get("avatar_url", f"https://ui-avatars.com/api/?name={member.get('full_name', 'U')}&background=random")
        })
    return directory

@router.post("/directory")
async def add_staff(payload: dict = Body(...), current_admin: dict = Depends(get_current_admin)):
    db = get_database()
    
    # Check if email exists
    existing = await db["users"].find_one({"email": payload.get("email")})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_password = get_password_hash(payload.get("password", "password123"))
    
    new_staff = {
        "full_name": payload.get("name"),
        "email": payload.get("email"),
        "phone": payload.get("phone", ""),
        "role": payload.get("role", "admin").lower(),
        "hashed_password": hashed_password,
        "department": payload.get("department", "Operations"),
        "designation": payload.get("designation", "Staff"),
        "salary": int(payload.get("salary", 45000)),
        "status": "Active",
        "saved_addresses": [],
        "created_at": datetime.utcnow()
    }
    
    result = await db["users"].insert_one(new_staff)
    
    # add employee_id back
    employee_id = f"EMP-{str(result.inserted_id)[-6:].upper()}"
    await db["users"].update_one({"_id": result.inserted_id}, {"$set": {"employee_id": employee_id}})
    
    return {"message": "Staff added successfully", "id": str(result.inserted_id)}

@router.put("/directory/{id}")
async def update_staff(id: str, payload: dict = Body(...), current_admin: dict = Depends(get_current_admin)):
    db = get_database()
    update_data = {
        "full_name": payload.get("name"),
        "phone": payload.get("phone"),
        "department": payload.get("department"),
        "designation": payload.get("designation"),
        "role": payload.get("role", "").lower()
    }
    # remove None values
    update_data = {k: v for k, v in update_data.items() if v is not None}
    
    result = await db["users"].update_one({"_id": ObjectId(id)}, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Staff not found or no changes made")
    return {"message": "Staff updated successfully"}

# ──────────────────────────────────────────────────────────
# ATTENDANCE
# ──────────────────────────────────────────────────────────
@router.get("/attendance")
async def get_attendance_logs(current_admin: dict = Depends(get_current_admin)):
    db = get_database()
    logs = await db["hrms_attendance"].find().sort("created_at", -1).to_list(100)
    
    # map user names if needed
    for log in logs:
        log["_id"] = str(log["_id"])
    return logs

@router.post("/attendance/clock-in")
async def clock_in(current_admin: dict = Depends(get_current_admin)):
    db = get_database()
    user_id = current_admin["id"]
    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    now = datetime.utcnow()
    # IST roughly
    now_ist = now + timedelta(hours=5, minutes=30)
    date_str = now_ist.strftime("%Y-%m-%d")
    time_str = now_ist.strftime("%I:%M %p")
    
    # Check if already clocked in today
    existing = await db["hrms_attendance"].find_one({"user_id": user_id, "date": date_str})
    if existing:
        raise HTTPException(status_code=400, detail="Already clocked in today")
        
    # logic for late
    is_late = now_ist.hour > 9 or (now_ist.hour == 9 and now_ist.minute > 30)
    status = "Late" if is_late else "Present"
    
    entry = {
        "user_id": user_id,
        "employee_id": user.get("employee_id", f"EMP-{user_id[-6:].upper()}"),
        "name": user.get("full_name", "Unknown"),
        "date": date_str,
        "status": status,
        "clock_in": time_str,
        "clock_out": "-",
        "working_hours": "-",
        "created_at": now
    }
    
    await db["hrms_attendance"].insert_one(entry)
    return {"message": "Clocked in successfully"}

@router.post("/attendance/clock-out")
async def clock_out(current_admin: dict = Depends(get_current_admin)):
    db = get_database()
    user_id = current_admin["id"]
    
    now = datetime.utcnow()
    now_ist = now + timedelta(hours=5, minutes=30)
    date_str = now_ist.strftime("%Y-%m-%d")
    time_str = now_ist.strftime("%I:%M %p")
    
    existing = await db["hrms_attendance"].find_one({"user_id": user_id, "date": date_str})
    if not existing:
        raise HTTPException(status_code=400, detail="Not clocked in today")
        
    if existing["clock_out"] != "-":
        raise HTTPException(status_code=400, detail="Already clocked out today")
        
    # crude hours calculation
    try:
        cin = datetime.strptime(existing["clock_in"], "%I:%M %p")
        cout = datetime.strptime(time_str, "%I:%M %p")
        diff = cout - cin
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        working_hours = f"{hours}h {minutes}m"
    except:
        working_hours = "Unknown"
        
    await db["hrms_attendance"].update_one(
        {"_id": existing["_id"]},
        {"$set": {"clock_out": time_str, "working_hours": working_hours}}
    )
    return {"message": "Clocked out successfully"}

# ──────────────────────────────────────────────────────────
# LEAVES
# ──────────────────────────────────────────────────────────
@router.get("/leaves")
async def get_leave_requests(current_admin: dict = Depends(get_current_admin)):
    db = get_database()
    leaves = await db["hrms_leaves"].find().sort("created_at", -1).to_list(100)
    for l in leaves:
        l["id"] = str(l["_id"])
        del l["_id"]
    return leaves

@router.post("/leaves")
async def apply_leave(payload: dict = Body(...), current_admin: dict = Depends(get_current_admin)):
    db = get_database()
    user_id = current_admin["id"]
    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    
    try:
        d1 = datetime.strptime(payload["from"], "%Y-%m-%d")
        d2 = datetime.strptime(payload["to"], "%Y-%m-%d")
        days = (d2 - d1).days + 1
    except:
        days = 1
        
    entry = {
        "user_id": user_id,
        "name": user.get("full_name", "Unknown"),
        "type": payload.get("type", "Casual Leave"),
        "from": payload.get("from"),
        "to": payload.get("to"),
        "days": days,
        "status": "Pending",
        "reason": payload.get("reason", ""),
        "created_at": datetime.utcnow()
    }
    
    await db["hrms_leaves"].insert_one(entry)
    return {"message": "Leave applied successfully"}

@router.put("/leaves/{id}/status")
async def update_leave_status(id: str, payload: dict = Body(...), current_admin: dict = Depends(get_current_admin)):
    db = get_database()
    status = payload.get("status")
    if status not in ["Approved", "Rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status")
        
    result = await db["hrms_leaves"].update_one({"_id": ObjectId(id)}, {"$set": {"status": status}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Leave not found")
    return {"message": f"Leave {status.lower()} successfully"}

# ──────────────────────────────────────────────────────────
# TASKS
# ──────────────────────────────────────────────────────────
@router.get("/tasks")
async def get_staff_tasks(current_admin: dict = Depends(get_current_admin)):
    db = get_database()
    tasks = await db["hrms_tasks"].find().sort("created_at", -1).to_list(100)
    for t in tasks:
        t["id"] = str(t["_id"])
        del t["_id"]
    return tasks

@router.post("/tasks")
async def add_task(payload: dict = Body(...), current_admin: dict = Depends(get_current_admin)):
    db = get_database()
    
    entry = {
        "title": payload.get("title"),
        "assignee": payload.get("assignee"),
        "assignee_id": payload.get("assignee_id"),
        "priority": payload.get("priority", "Medium"),
        "deadline": payload.get("deadline"),
        "status": "Pending",
        "created_at": datetime.utcnow()
    }
    
    await db["hrms_tasks"].insert_one(entry)
    return {"message": "Task assigned successfully"}

@router.put("/tasks/{id}/status")
async def update_task_status(id: str, payload: dict = Body(...), current_admin: dict = Depends(get_current_admin)):
    db = get_database()
    status = payload.get("status")
        
    result = await db["hrms_tasks"].update_one({"_id": ObjectId(id)}, {"$set": {"status": status}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": f"Task status updated to {status}"}

# ──────────────────────────────────────────────────────────
# PAYROLL (Simulated but reads dynamic base salary)
# ──────────────────────────────────────────────────────────
@router.get("/payroll")
async def get_payroll_data(current_admin: dict = Depends(get_current_admin)):
    db = get_database()
    staff = await db["users"].find({"role": {"$ne": "customer"}}).to_list(1000)
    
    payroll = []
    for idx, s in enumerate(staff):
        base = s.get("salary", 45000)
        allowance = base * 0.2
        deduction = base * 0.05
        net = base + allowance - deduction
        payroll.append({
            "id": str(s.get("_id")),
            "employee_id": s.get("employee_id", f"EMP-{str(s.get('_id'))[-6:].upper()}"),
            "name": s.get("full_name", "Unknown"),
            "month": datetime.utcnow().strftime("%B %Y"),
            "basic_salary": base,
            "allowances": allowance,
            "deductions": deduction,
            "net_salary": net,
            "status": "Processed"
        })
    return payroll
