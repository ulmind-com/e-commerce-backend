import asyncio
import re
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = "mongodb+srv://db_user:abc1%4023@cluster0.2zwacid.mongodb.net/"
DATABASE_NAME = "ecommerce"

async def main():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    products = await db.products.find({}).to_list(None)
    
    # We will use this dictionary to find related Unsplash images based on keywords in title
    image_pool = {
        "plant": [
            "https://images.unsplash.com/photo-1416879598555-2272af1758c0?w=600&q=80",
            "https://images.unsplash.com/photo-1497250681960-ef046c08a56e?w=600&q=80",
            "https://images.unsplash.com/photo-1459156212016-c812468e2115?w=600&q=80",
            "https://images.unsplash.com/photo-1545241047-6083a36a1c08?w=600&q=80"
        ],
        "cocktail": [
            "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=600&q=80",
            "https://images.unsplash.com/photo-1536935338788-846bb9981813?w=600&q=80",
            "https://images.unsplash.com/photo-1551538827-9c037cb4f32a?w=600&q=80"
        ],
        "drink": [
            "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=600&q=80",
            "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=600&q=80"
        ],
        "food": [
            "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=600&q=80",
            "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=600&q=80",
            "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=600&q=80"
        ],
        "grocery": [
            "https://images.unsplash.com/photo-1542838132-92c53300491e?w=600&q=80",
            "https://images.unsplash.com/photo-1578916171728-46686eac8d58?w=600&q=80"
        ],
        "default": [
            "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&q=80",
            "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&q=80",
            "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=600&q=80"
        ]
    }
    
    updated_count = 0
    for p in products:
        images = p.get("image_urls", [])
        if len(images) < 3:
            title = p.get("title", "").lower()
            desc = p.get("description", "").lower()
            text = title + " " + desc
            
            pool = image_pool["default"]
            if "plant" in text or "tree" in text or "flower" in text:
                pool = image_pool["plant"]
            elif "cocktail" in text or "margarita" in text or "vodka" in text or "wine" in text:
                pool = image_pool["cocktail"]
            elif "drink" in text or "juice" in text or "cola" in text or "water" in text:
                pool = image_pool["drink"]
            elif "food" in text or "snack" in text or "bread" in text or "chips" in text:
                pool = image_pool["food"]
            elif "grocery" in text or "rice" in text or "dal" in text or "atta" in text:
                pool = image_pool["grocery"]
            
            # Make sure we don't add duplicates
            new_images = images.copy()
            for img in pool:
                if img not in new_images:
                    new_images.append(img)
                if len(new_images) >= 3:
                    break
            
            await db.products.update_one({"_id": p["_id"]}, {"$set": {"image_urls": new_images}})
            updated_count += 1
            print(f"Updated '{title}' with {len(new_images)} images.")
            
    print(f"Finished updating {updated_count} products.")
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
