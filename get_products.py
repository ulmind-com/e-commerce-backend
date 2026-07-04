import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import json

MONGODB_URL = "mongodb+srv://db_user:abc1%4023@cluster0.2zwacid.mongodb.net/"
DATABASE_NAME = "ecommerce"

async def main():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    products = await db.products.find({}).to_list(None)
    titles = [p.get("title", "") for p in products]
    
    print(json.dumps(titles, indent=2))
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
