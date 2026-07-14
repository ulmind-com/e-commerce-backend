import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    client = AsyncIOMotorClient("mongodb+srv://arnabsenapati63:B49fQzBpxN2eS9F4@cluster0.0vldy.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["onebasket"]
    count = await db["orders"].count_documents({"order_status": "Cancelled"})
    print(f"Cancelled orders: {count}")

asyncio.run(main())
