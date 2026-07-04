import asyncio
from app.core.db import connect_to_mongo, get_database, close_mongo_connection

async def main():
    await connect_to_mongo()
    db = get_database()
    user = await db["users"].find_one({"email": "swastikaroytitu@gmail.com"})
    print("User:", user)
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(main())
