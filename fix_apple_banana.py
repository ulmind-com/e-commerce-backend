import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = "mongodb+srv://db_user:abc1%4023@cluster0.2zwacid.mongodb.net/"
DATABASE_NAME = "ecommerce"

IMG_APPLE_1 = "https://upload.wikimedia.org/wikipedia/commons/1/15/Red_Apple.jpg"
IMG_APPLE_2 = "https://upload.wikimedia.org/wikipedia/commons/8/88/Bright_red_tomato_and_cross_section02.jpg"
IMG_BANANA_1 = "https://upload.wikimedia.org/wikipedia/commons/9/98/Bananas_on_black_background_02.jpg"
IMG_BANANA_2 = "https://upload.wikimedia.org/wikipedia/commons/3/31/Cavendish_banana_from_Maracaibo.jpg"
IMG_LIZOL_1 = "https://upload.wikimedia.org/wikipedia/commons/9/9c/Blue_bucket_with_Bruce_hardwood_floor_cleaner.jpg"
IMG_LIZOL_2 = "https://upload.wikimedia.org/wikipedia/commons/b/b9/Mr._Clean.jpg"

FIXES = {
    "Fresh Kashmiri Apple": [IMG_APPLE_1, IMG_APPLE_2],
    "Robusta Banana": [IMG_BANANA_1, IMG_BANANA_2],
    "lizol": [IMG_LIZOL_1, IMG_LIZOL_2],
}

async def main():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    for title, urls in FIXES.items():
        await db.products.update_one({"title": title}, {"$set": {"image_urls": urls}})
        print(f"Fixed {title} with unique Wiki Images")
        
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
