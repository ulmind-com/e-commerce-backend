from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Any
from app.models.category import CategoryCreate, CategoryResponse, CategoryInDB, CategoryBase
from app.core.security import get_current_admin
from app.core.db import get_database
import uuid

router = APIRouter()


def _serialize_cat(doc: dict) -> dict:
    """Convert MongoDB category document to JSON-serializable dict."""
    if doc is None:
        return None
    d = dict(doc)
    if "_id" in d:
        d["_id"] = str(d["_id"])
    return d


@router.get("/", response_model=List[CategoryResponse])
async def read_categories():
    db = get_database()
    cats = await db["categories"].find({"is_active": True}).to_list(100)
    return [_serialize_cat(c) for c in cats]


@router.post("/", response_model=CategoryResponse, dependencies=[Depends(get_current_admin)])
async def create_category(category_in: CategoryCreate):
    db = get_database()
    category_dict = category_in.model_dump()
    category_dict["_id"] = str(uuid.uuid4())
    db_category = CategoryInDB(**category_dict)
    await db["categories"].insert_one(db_category.model_dump(by_alias=True))
    return db_category


@router.put("/{category_id}", response_model=CategoryResponse, dependencies=[Depends(get_current_admin)])
async def update_category(category_id: str, category_in: CategoryBase):
    db = get_database()
    # Support ObjectId
    filter_q = {"_id": category_id}
    try:
        from bson import ObjectId
        if ObjectId.is_valid(category_id):
            filter_q = {"_id": ObjectId(category_id)}
    except Exception:
        pass
    update_data = category_in.model_dump(exclude_unset=True)
    result = await db["categories"].update_one(filter_q, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Category not found or no changes")
    updated = await db["categories"].find_one(filter_q)
    return _serialize_cat(updated)


@router.delete("/{category_id}", dependencies=[Depends(get_current_admin)])
async def delete_category(category_id: str):
    db = get_database()
    filter_q = {"_id": category_id}
    try:
        from bson import ObjectId
        if ObjectId.is_valid(category_id):
            filter_q = {"_id": ObjectId(category_id)}
    except Exception:
        pass
    result = await db["categories"].delete_one(filter_q)
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"msg": "Category deleted successfully"}
