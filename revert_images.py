import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = "mongodb+srv://db_user:abc1%4023@cluster0.2zwacid.mongodb.net/"
DATABASE_NAME = "ecommerce"

async def revert():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    products = await db.products.find({}).to_list(None)
    for p in products:
        images = p.get("image_urls", [])
        if len(images) > 1:
            # We appended the fake images, so the first one is the original correct one.
            # We will keep only the first image.
            await db.products.update_one({"_id": p["_id"]}, {"$set": {"image_urls": [images[0]]}})
            
    print("Successfully reverted all products to their original single image.")
    client.close()

if __name__ == "__main__":
    asyncio.run(revert())
