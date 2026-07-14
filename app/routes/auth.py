from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from app.models.user import UserCreate, UserResponse, UserInDB
from app.core.security import get_password_hash, verify_password, create_access_token, get_current_user
from app.core.db import get_database
from app.services.cloudinary_service import upload_avatar
from pydantic import BaseModel
from typing import Any, Optional
from datetime import datetime
import uuid
import asyncio
from functools import partial

router = APIRouter()

class GoogleAuthRequest(BaseModel):
    email: str
    full_name: str
    avatar_url: Optional[str] = None
    uid: str

@router.post("/google")
async def google_auth(req: GoogleAuthRequest) -> Any:
    db = get_database()
    user = await db["users"].find_one({"email": req.email})
    
    if not user:
        import secrets
        random_password = secrets.token_urlsafe(32)
        user_id = str(uuid.uuid4())
        
        user_dict = {
            "_id": user_id,
            "email": req.email,
            "full_name": req.full_name,
            "role": "customer",
            "hashed_password": get_password_hash(random_password),
            "avatar_url": req.avatar_url,
            "saved_addresses": [],
            "created_at": datetime.utcnow()
        }
        await db["users"].insert_one(user_dict)
        user = user_dict
    else:
        if not user.get("avatar_url") and req.avatar_url:
            await db["users"].update_one({"_id": user["_id"]}, {"$set": {"avatar_url": req.avatar_url}})
            user["avatar_url"] = req.avatar_url

    access_token = create_access_token(data={"sub": user["_id"], "role": user.get("role", "customer")})
    return {"access_token": access_token, "token_type": "bearer", "role": user.get("role", "customer"), "id": user["_id"]}


@router.post("/register", response_model=UserResponse)
async def register(user_in: UserCreate) -> Any:
    db = get_database()
    user = await db["users"].find_one({"email": user_in.email})
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user_dict = user_in.model_dump(exclude={"password"})
    user_dict["hashed_password"] = get_password_hash(user_in.password)
    user_dict["_id"] = str(uuid.uuid4())

    db_user = UserInDB(**user_dict)
    await db["users"].insert_one(db_user.model_dump(by_alias=True))

    return db_user


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    try:
        db = get_database()
        user = await db["users"].find_one({"email": form_data.username})
        if not user or not verify_password(form_data.password, user["hashed_password"]):
            raise HTTPException(status_code=400, detail="Incorrect email or password")

        access_token = create_access_token(data={"sub": user["_id"], "role": user.get("role", "customer")})
        return {"access_token": access_token, "token_type": "bearer", "role": user.get("role", "customer"), "id": user["_id"]}
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        raise HTTPException(status_code=500, detail=tb)


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_user)) -> Any:
    db = get_database()
    user = await db["users"].find_one({"_id": current_user["id"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None

@router.put("/me", response_model=UserResponse)
async def update_profile(
    req: ProfileUpdateRequest,
    current_user: dict = Depends(get_current_user)
) -> Any:
    db = get_database()
    update_data = {}
    if req.full_name is not None:
        update_data["full_name"] = req.full_name
    if req.phone is not None:
        update_data["phone"] = req.phone
        
    if update_data:
        await db["users"].update_one(
            {"_id": current_user["id"]},
            {"$set": update_data}
        )
        
    user = await db["users"].find_one({"_id": current_user["id"]})
    return user


@router.post("/me/avatar")
async def upload_user_avatar(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
) -> Any:
    """Upload or replace the authenticated user's profile picture on Cloudinary."""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    user_id = current_user["id"]
    file_bytes = await file.read()

    loop = asyncio.get_event_loop()
    avatar_url = await loop.run_in_executor(
        None,
        partial(upload_avatar, file_bytes, user_id)
    )

    if not avatar_url:
        raise HTTPException(status_code=400, detail="Failed to upload avatar to Cloudinary")

    db = get_database()
    await db["users"].update_one(
        {"_id": user_id},
        {"$set": {"avatar_url": avatar_url}}
    )
    return {"avatar_url": avatar_url}


@router.post("/me/addresses", response_model=UserResponse)
async def add_saved_address(
    address: dict,
    current_user: dict = Depends(get_current_user)
) -> Any:
    db = get_database()
    # Add an ID to the address
    address["id"] = str(uuid.uuid4())
    
    await db["users"].update_one(
        {"_id": current_user["id"]},
        {"$push": {"saved_addresses": address}}
    )
    
    user = await db["users"].find_one({"_id": current_user["id"]})
    return user


@router.delete("/me/addresses/{address_id}", response_model=UserResponse)
async def delete_saved_address(
    address_id: str,
    current_user: dict = Depends(get_current_user)
) -> Any:
    db = get_database()
    await db["users"].update_one(
        {"_id": current_user["id"]},
        {"$pull": {"saved_addresses": {"id": address_id}}}
    )
    
    user = await db["users"].find_one({"_id": current_user["id"]})
    return user


@router.put("/me/addresses/{address_id}", response_model=UserResponse)
async def edit_saved_address(
    address_id: str,
    address: dict,
    current_user: dict = Depends(get_current_user)
) -> Any:
    db = get_database()
    
    # Keep the same ID
    address["id"] = address_id
    
    # We use array filters to update the specific address object in the array
    await db["users"].update_one(
        {"_id": current_user["id"], "saved_addresses.id": address_id},
        {"$set": {"saved_addresses.$": address}}
    )
    
    user = await db["users"].find_one({"_id": current_user["id"]})
    return user

