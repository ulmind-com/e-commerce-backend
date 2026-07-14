from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from bson import ObjectId
from app.models.brand import BrandCreate, BrandResponse, BrandInDB
from app.core.db import get_database
from app.core.security import get_current_user

router = APIRouter()

@router.post("/", response_model=BrandResponse, status_code=status.HTTP_201_CREATED)
async def create_brand(brand: BrandCreate, current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db = get_database()
    brand_dict = brand.model_dump()
    
    # Check if slug exists
    if await db.brands.find_one({"slug": brand.slug}):
        raise HTTPException(status_code=400, detail="Brand with this slug already exists")
        
    result = await db.brands.insert_one(brand_dict)
    brand_dict["_id"] = str(result.inserted_id)
    return brand_dict

@router.get("/", response_model=List[BrandResponse])
async def get_brands():
    db = get_database()
    brands = await db.brands.find().to_list(1000)
    for brand in brands:
        brand["_id"] = str(brand["_id"])
    return brands

@router.get("/{brand_id}", response_model=BrandResponse)
async def get_brand(brand_id: str):
    db = get_database()
    brand = await db.brands.find_one({"_id": ObjectId(brand_id)})
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    brand["_id"] = str(brand["_id"])
    return brand

@router.put("/{brand_id}", response_model=BrandResponse)
async def update_brand(brand_id: str, brand_update: BrandCreate, current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    db = get_database()
    update_dict = brand_update.model_dump(exclude_unset=True)
    
    # Check slug collision
    existing = await db.brands.find_one({"slug": brand_update.slug})
    if existing and str(existing["_id"]) != brand_id:
        raise HTTPException(status_code=400, detail="Brand with this slug already exists")
        
    result = await db.brands.update_one(
        {"_id": ObjectId(brand_id)},
        {"$set": update_dict}
    )
    
    if result.modified_count == 0 and result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Brand not found")
        
    updated_brand = await db.brands.find_one({"_id": ObjectId(brand_id)})
    updated_brand["_id"] = str(updated_brand["_id"])
    return updated_brand

@router.delete("/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_brand(brand_id: str, current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    db = get_database()
    result = await db.brands.delete_one({"_id": ObjectId(brand_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Brand not found")
    return None
