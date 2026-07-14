import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGODB_URL")

async def make_admin():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client["onebasket"]
    
    # Update all users to have role 'admin' for testing, or just the specific user
    result = await db["users"].update_many({}, {"$set": {"role": "admin"}})
    print(f"Modified {result.modified_count} users to admin.")
    
if __name__ == "__main__":
    asyncio.run(make_admin())
