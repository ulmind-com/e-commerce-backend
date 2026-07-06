import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from app.core.security import get_password_hash
import uuid
from datetime import datetime

load_dotenv()
url = os.getenv('MONGODB_URL')

async def create_or_update_admin():
    client = AsyncIOMotorClient(url)
    db = client['ecommerce']
    
    email = "admin@onebasket.com"
    password = "password123"
    hashed_password = get_password_hash(password)
    
    user = await db.users.find_one({"email": email})
    
    if user:
        await db.users.update_one(
            {"email": email}, 
            {"$set": {"role": "admin", "hashed_password": hashed_password}}
        )
        print("Updated existing admin account.")
    else:
        user_dict = {
            "_id": str(uuid.uuid4()),
            "email": email,
            "full_name": "Admin User",
            "role": "admin",
            "hashed_password": hashed_password,
            "saved_addresses": [],
            "created_at": datetime.utcnow()
        }
        await db.users.insert_one(user_dict)
        print("Created new admin account.")

asyncio.run(create_or_update_admin())
