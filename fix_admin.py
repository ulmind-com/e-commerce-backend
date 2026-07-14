import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
import bcrypt

MONGODB_URL = "mongodb+srv://db_user:abc1%4023@cluster0.2zwacid.mongodb.net/"
DATABASE_NAME = "ecommerce_db" # Assuming it's ecommerce_db or similar? Wait, I need to check settings.DATABASE_NAME

import sys
sys.path.append("/Users/arnabsenapati/E-Commerce/e-commerce-backend")
from app.core.config import settings
from app.core.security import get_password_hash

async def fix_admin():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    
    admin_email = "admin@onebasket.com"
    admin_user = await db.users.find_one({"email": admin_email})
    
    hashed_pw = get_password_hash("admin123")
    
    if admin_user:
        print("Admin user exists. Updating password...")
        await db.users.update_one({"email": admin_email}, {"$set": {"hashed_password": hashed_pw, "role": "admin"}})
    else:
        print("Admin user not found. Creating...")
        await db.users.insert_one({
            "_id": "admin_1",
            "email": admin_email,
            "full_name": "Admin User",
            "role": "admin",
            "hashed_password": hashed_pw
        })
    print("Done")

if __name__ == "__main__":
    asyncio.run(fix_admin())
