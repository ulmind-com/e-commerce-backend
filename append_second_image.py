import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import requests

MONGODB_URL = "mongodb+srv://db_user:abc1%4023@cluster0.2zwacid.mongodb.net/"
DATABASE_NAME = "ecommerce"

# Verified generic images for each category
CATEGORY_IMAGES = {
    "Fresh Produce": "https://images.unsplash.com/photo-1542838132-92c53300491e?w=600&q=80",
    "Fresh Fruits": "https://images.unsplash.com/photo-1610832958506-aa56368176cf?w=600&q=80",
    "Dairy & Bakery": "https://images.unsplash.com/photo-1628088062854-d1870b4553da?w=600&q=80",
    "Dairy, Bread & Eggs": "https://images.unsplash.com/photo-1628088062854-d1870b4553da?w=600&q=80",
    "Beverages": "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=600&q=80",
    "Snacks": "https://images.unsplash.com/photo-1599818826500-2d8816c21e64?w=600&q=80",
    "Personal Care": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=600&q=80",
    "Pharmacy": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=600&q=80",
    "Staples & Grocery": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=600&q=80",
    "Pet Care": "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=600&q=80", # Dog
    "Baby Care": "https://images.unsplash.com/photo-1555252136-1e6d4c6731be?w=600&q=80",
}

async def main():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    # Pre-fetch category names to map IDs to names
    categories = await db.categories.find({}).to_list(None)
    cat_map = {str(c["_id"]): c["name"] for c in categories}
    
    products = await db.products.find({}).to_list(None)
    
    count = 0
    for p in products:
        images = p.get("image_urls", [])
        if len(images) > 0:
            # Get the category name
            cat_id = str(p.get("category_id", ""))
            cat_name = cat_map.get(cat_id, p.get("category", ""))
            
            # Find the generic image for this category
            generic_img = CATEGORY_IMAGES.get(cat_name, "https://images.unsplash.com/photo-1542838132-92c53300491e?w=600&q=80")
            
            # Only keep the FIRST original image, and append the generic one
            new_images = [images[0], generic_img]
            
            await db.products.update_one({"_id": p["_id"]}, {"$set": {"image_urls": new_images}})
            count += 1
            
    print(f"Successfully added reliable secondary images to {count} products.")
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
