import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('MONGODB_URL')

async def make_admin():
    client = AsyncIOMotorClient(url)
    db = client['ecommerce_db']
    await db.users.update_one({'email': 'admin@onebasket.com'}, {'$set': {'role': 'admin'}})
    print('Updated role to admin.')

asyncio.run(make_admin())
