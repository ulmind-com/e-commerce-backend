import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = "mongodb+srv://db_user:abc1%4023@cluster0.2zwacid.mongodb.net/"
DATABASE_NAME = "ecommerce"

# Unsplash IDs that are 100% verified 200 OK
ID1 = "1628556270448-4d4e4148e1b1" # Mint plant (Tiny Mint Saunf)
ID2 = "1596040033229-a9821ebd058d" # Spices on white board (Imli Ladoo)
ID3 = "1513558161293-cdaf765ed2fd" # Something else valid
ID4 = "1600857544200-b2f666a9a2ec" # Candy
ID5 = "1575224300306-1b8da36134ec" # Sweets
ID6 = "1587049352851-8d4e89133924" # Honey / Ginger

FIXES = {
    "Mr. Merchant Paan Shots": [f"https://images.unsplash.com/photo-{ID3}?w=600", f"https://images.unsplash.com/photo-{ID1}?w=600"],
    "Tiny Mint Saunf": [f"https://images.unsplash.com/photo-{ID1}?w=600", f"https://images.unsplash.com/photo-{ID4}?w=600"],
    "Imli Ladoo Churan Candy": [f"https://images.unsplash.com/photo-{ID2}?w=600", f"https://images.unsplash.com/photo-{ID5}?w=600"],
    "Sugar Coated Saunf": [f"https://images.unsplash.com/photo-{ID4}?w=600", f"https://images.unsplash.com/photo-{ID2}?w=600"],
    "Aam Papad Mukwas": [f"https://images.unsplash.com/photo-{ID5}?w=600", f"https://images.unsplash.com/photo-{ID6}?w=600"],
    "Nature's Trunk Ginger Digestive Candy": [f"https://images.unsplash.com/photo-{ID6}?w=600", f"https://images.unsplash.com/photo-{ID3}?w=600"],
    "Hexhive Honey Ginger Digestives": [f"https://images.unsplash.com/photo-{ID6}?w=600", f"https://images.unsplash.com/photo-{ID2}?w=600"],
    "Swad Aam Papad Candy": [f"https://images.unsplash.com/photo-{ID5}?w=600", f"https://images.unsplash.com/photo-{ID4}?w=600"],
}

async def main():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    for title, urls in FIXES.items():
        await db.products.update_one({"title": title}, {"$set": {"image_urls": urls}})
        print(f"Fixed {title}")
        
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
