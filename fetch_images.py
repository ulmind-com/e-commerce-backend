import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from duckduckgo_search import DDGS

MONGODB_URL = "mongodb+srv://db_user:abc1%4023@cluster0.2zwacid.mongodb.net/"
DATABASE_NAME = "ecommerce"

async def main():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    products = await db.products.find({}).to_list(None)
    updated_count = 0
    
    with DDGS() as ddgs:
        for p in products:
            images = p.get("image_urls", [])
            # We want at least 2 or 3 images
            if len(images) < 2:
                title = p.get("title", "")
                print(f"Searching images for: {title}")
                try:
                    # Search for the product name
                    results = ddgs.images(title, max_results=3)
                    new_images = images.copy()
                    
                    for r in results:
                        img_url = r.get('image')
                        if img_url and img_url not in new_images:
                            new_images.append(img_url)
                        if len(new_images) >= 3:
                            break
                            
                    if len(new_images) > len(images):
                        await db.products.update_one({"_id": p["_id"]}, {"$set": {"image_urls": new_images}})
                        updated_count += 1
                        print(f" -> Added {len(new_images) - len(images)} images.")
                except Exception as e:
                    print(f"Error searching for {title}: {e}")
                    
    print(f"Finished updating {updated_count} products.")
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
