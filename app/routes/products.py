from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import List, Any, Optional
from app.models.product import ProductCreate, ProductResponse, ProductInDB, ProductBase
from app.core.security import get_current_admin
from app.core.db import get_database
from app.services.cloudinary_service import upload_image, delete_image, get_public_id_from_url
import uuid
import asyncio
from functools import partial
import urllib.request
import re
from app.services.recommendation_service import get_similar_products

router = APIRouter()

def get_unsplash_id(query):
    query_slug = query.replace(" ", ",")
    url = f'https://loremflickr.com/400/400/{query_slug}'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req)
        return resp.url # Resolve redirect to get final static image URL
    except Exception as e:
        pass
    return None


def _serialize(doc: dict) -> dict:
    """Convert MongoDB document to JSON-serializable dict.
    Handles ObjectId _id by converting to string."""
    if doc is None:
        return None
    d = dict(doc)
    if "_id" in d:
        d["_id"] = str(d["_id"])
    return d


async def _find_product(db, product_id: str):
    """Try to find a product by string _id first, then by ObjectId."""
    # Try direct string match first (UUID-based IDs created via API)
    product = await db["products"].find_one({"_id": product_id})
    if product:
        return _serialize(product)

    # Try ObjectId (seeded products inserted by seed scripts)
    try:
        from bson import ObjectId
        if ObjectId.is_valid(product_id):
            product = await db["products"].find_one({"_id": ObjectId(product_id)})
            if product:
                return _serialize(product)
    except Exception:
        pass

    return None


@router.get("", response_model=List[ProductResponse])
async def read_products(skip: int = 0, limit: int = 100, category_id: Optional[str] = None):
    db = get_database()
    query = {"is_published": True}
    if category_id:
        query["category_id"] = category_id
    raw = await db["products"].find(query).skip(skip).limit(limit).to_list(100)
    return [_serialize(p) for p in raw]


@router.get("/{product_id}", response_model=ProductResponse)
async def read_product(product_id: str):
    db = get_database()
    product = await _find_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("", response_model=ProductResponse, dependencies=[Depends(get_current_admin)])
async def create_product(product_in: ProductCreate):
    db = get_database()
    product_dict = product_in.model_dump()
    product_dict["_id"] = str(uuid.uuid4())

    # AI Auto-Image Fetching
    if not product_dict.get("image_urls"):
        loop = asyncio.get_event_loop()
        image_url = await loop.run_in_executor(None, get_unsplash_id, product_dict.get("title", ""))
        if image_url:
            product_dict["image_urls"] = [image_url]

    db_product = ProductInDB(**product_dict)
    await db["products"].insert_one(db_product.model_dump(by_alias=True))
    return db_product


@router.post("/{product_id}/image", dependencies=[Depends(get_current_admin)])
async def upload_product_image(product_id: str, file: UploadFile = File(...)):
    """Upload an image for a product to Cloudinary and store the URL in MongoDB."""
    db = get_database()
    product = await _find_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    file_bytes = await file.read()
    loop = asyncio.get_event_loop()
    image_url = await loop.run_in_executor(
        None,
        partial(upload_image, file_bytes, "ecommerce/products")
    )

    if not image_url:
        raise HTTPException(status_code=400, detail="Failed to upload image to Cloudinary")

    # Update using both string and ObjectId filter
    await db["products"].update_one(
        {"_id": product["_id"]},
        {"$push": {"image_urls": image_url}}
    )
    return {"image_url": image_url, "product_id": product_id}


@router.delete("/{product_id}/image", dependencies=[Depends(get_current_admin)])
async def delete_product_image(product_id: str, image_url: str):
    """Remove an image URL from the product and delete it from Cloudinary."""
    db = get_database()
    product = await _find_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if image_url not in product.get("image_urls", []):
        raise HTTPException(status_code=404, detail="Image URL not found on this product")

    public_id = get_public_id_from_url(image_url)
    if public_id:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, partial(delete_image, public_id))

    await db["products"].update_one(
        {"_id": product["_id"]},
        {"$pull": {"image_urls": image_url}}
    )
    return {"msg": "Image deleted successfully", "product_id": product_id}


@router.put("/{product_id}", response_model=ProductResponse, dependencies=[Depends(get_current_admin)])
async def update_product(product_id: str, product_in: ProductBase):
    db = get_database()
    existing = await _find_product(db, product_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Product not found")
    update_data = product_in.model_dump(exclude_unset=True)
    await db["products"].update_one({"_id": existing["_id"]}, {"$set": update_data})
    updated = await _find_product(db, product_id)
    return updated


@router.delete("/{product_id}", dependencies=[Depends(get_current_admin)])
async def delete_product(product_id: str):
    db = get_database()
    existing = await _find_product(db, product_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Product not found")
    result = await db["products"].delete_one({"_id": existing["_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"msg": "Product deleted successfully"}


@router.get("/{product_id}/similar", response_model=List[ProductResponse])
async def get_similar_products_route(product_id: str):
    db = get_database()
    
    # 1. Fetch target product
    target_product = await _find_product(db, product_id)
    if not target_product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    # 2. Fetch candidates (same category)
    category_id = target_product.get("category_id")
    query = {"is_published": True}
    if category_id:
        query["category_id"] = category_id
        
    candidates_raw = await db["products"].find(query).limit(50).to_list(50)
    candidates = [_serialize(p) for p in candidates_raw]
    
    # If not enough candidates in same category, just fetch any
    if len(candidates) < 5:
        candidates_raw = await db["products"].find({"is_published": True}).limit(50).to_list(50)
        candidates = [_serialize(p) for p in candidates_raw]
        
    # 3. Call Groq service
    similar_ids = get_similar_products(target_product, candidates)
    
    # 4. Fetch the actual products based on IDs
    similar_products = []
    if similar_ids:
        # Get products in a single query
        from bson import ObjectId
        
        # Build query for both string UUIDs and ObjectIds
        object_ids = []
        string_ids = []
        for sid in similar_ids:
            string_ids.append(sid)
            try:
                if ObjectId.is_valid(sid):
                    object_ids.append(ObjectId(sid))
            except:
                pass
                
        id_query = {"$or": [{"_id": {"$in": string_ids}}]}
        if object_ids:
            id_query["$or"].append({"_id": {"$in": object_ids}})
            
        final_raw = await db["products"].find(id_query).to_list(10)
        similar_products = [_serialize(p) for p in final_raw]
        
    # Sort them to match the Groq output order if possible
    # We'll just return what we have
    return similar_products

