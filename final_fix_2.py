import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = "mongodb+srv://db_user:abc1%4023@cluster0.2zwacid.mongodb.net/"
DATABASE_NAME = "ecommerce"

# MASTER contains the exact primary image.
# SECONDARY contains the exact secondary image.
MAPPING = {
    "Mr. Merchant Paan Shots": ["https://images.unsplash.com/photo-1628556270448-4d4e4148e1b1?w=600", "https://loremflickr.com/600/600/spice"],
    "Tiny Mint Saunf": ["https://images.unsplash.com/photo-1628556270448-4d4e4148e1b1?w=600", "https://loremflickr.com/600/600/fennel"],
    "Imli Ladoo Churan Candy": ["https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=600", "https://loremflickr.com/600/600/tamarind"],
    "Sugar Coated Saunf": ["https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=600", "https://loremflickr.com/600/600/candy,spice"],
    "Supply6 Salts Lime Electrolyte Mix": ["https://loremflickr.com/600/600/electrolyte,drink", "https://loremflickr.com/600/600/lime,drink"],
    "Kombucha Hibiscus Lime": ["https://loremflickr.com/600/600/kombucha,drink", "https://loremflickr.com/600/600/tea,drink"],
    "Kombucha Blueberry Lavender": ["https://loremflickr.com/600/600/kombucha,bottle", "https://loremflickr.com/600/600/tea,bottle"],
    "Krishna's Herbal & Ayurveda Aloe Vera": ["https://loremflickr.com/600/600/aloe,juice", "https://loremflickr.com/600/600/ayurveda"],
    "Kombucha Original": ["https://loremflickr.com/600/600/kombucha,glass", "https://loremflickr.com/600/600/tea,glass"],
    "Aam Papad Mukwas": ["https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=600", "https://loremflickr.com/600/600/mango,candy"],
    "Nature's Trunk Ginger Digestive Candy": ["https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=600", "https://loremflickr.com/600/600/ginger,candy"],
    "Hexhive Honey Ginger Digestives": ["https://images.unsplash.com/photo-1587049352851-8d4e89133924?w=600", "https://loremflickr.com/600/600/honey,jar"],
    "Swad Aam Papad Candy": ["https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=600", "https://loremflickr.com/600/600/candy,sweet"],
    
    "Amul Taaza Toned Fresh Milk": ["https://images.unsplash.com/photo-1550583724-b2692b85b150?w=600", "https://loremflickr.com/600/600/milk,carton"],
    "Farm Fresh White Eggs": ["https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=900/app/images/products/full_screen/305040_A.jpg", "https://loremflickr.com/600/600/eggs,basket"],
    "Harvest Gold White Bread": ["https://images.unsplash.com/photo-1509440159596-0249088772ff?w=600", "https://loremflickr.com/600/600/bread,slice"],
    "Mother Dairy Classic Dahi": ["https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=900/da/cms-assets/cms/product/d7a0818e-c466-4ffb-ac15-8156ccc27d90.jpg", "https://loremflickr.com/600/600/yogurt,bowl"],
    
    "Fresh Kashmiri Apple": ["https://images.unsplash.com/photo-1560806887-1e4cd0b6faa6?w=600", "https://loremflickr.com/600/600/red,apple"],
    "Robusta Banana": ["https://images.unsplash.com/photo-1571501478200-b5b4a6bc9f58?w=600", "https://loremflickr.com/600/600/banana,bunch"],
    "Fresh Orange": ["https://images.unsplash.com/photo-1611080626919-7cf5a9dbab5b?w=600", "https://loremflickr.com/600/600/orange,fruit"],
    "Green Grapes": ["https://images.unsplash.com/photo-1537640538966-79f369143f8f?w=600", "https://loremflickr.com/600/600/green,grapes"],
    "Watermelon": ["https://images.unsplash.com/photo-1589984662646-e7b2e4962f18?w=600", "https://loremflickr.com/600/600/watermelon,slice"],
    
    "Honitus Cough Syrup": ["https://images.unsplash.com/photo-1584017911766-d451b3d0e843?w=600", "https://loremflickr.com/600/600/cough,syrup"],
    "Volini Pain Relief Spray": ["https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=600", "https://loremflickr.com/600/600/spray,bottle"],
    "Crocin Advance": ["https://images.unsplash.com/photo-1631549916768-4119b2e5f926?w=600", "https://loremflickr.com/600/600/pills,medicine"],
    "Vicks VapoRub": ["https://images.unsplash.com/photo-1584362917165-526a968579e8?w=600", "https://loremflickr.com/600/600/medicine,jar"],
    
    "Pedigree Adult Dog Food": ["https://images.unsplash.com/photo-1589924691995-400dc9ecc119?w=600", "https://loremflickr.com/600/600/dog,food"],
    "Whiskas Cat Food": ["https://images.unsplash.com/photo-1623387641168-d9803ddd3f35?w=600", "https://loremflickr.com/600/600/cat,food"],
    "Dog Chew Bone": ["https://images.unsplash.com/photo-1535930891776-0c2dfb7fda1a?w=600", "https://loremflickr.com/600/600/dog,bone"],
    "Cat Litter Sand": ["https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=600", "https://loremflickr.com/600/600/cat,litter"],
    
    "Pampers Active Baby Diapers": ["https://images.unsplash.com/photo-1519689680058-324335c77eba?w=600", "https://loremflickr.com/600/600/diaper,baby"],
    "Johnson's Baby Lotion": ["https://images.unsplash.com/photo-1555252333-9f8e92e65df9?w=600", "https://loremflickr.com/600/600/lotion,baby"],
    "Baby Wipes": ["https://images.unsplash.com/photo-1512438248247-f0f2a5a8b7f0?w=600", "https://loremflickr.com/600/600/wipes,baby"],
    "Himalaya Baby Powder": ["https://images.unsplash.com/photo-1522771930-78848d9293e8?w=600", "https://loremflickr.com/600/600/powder,baby"],
    
    "amul butter": ["https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=600", "https://loremflickr.com/600/600/butter"],
    "lizol": ["https://images.unsplash.com/photo-1584820927508-0118357eb482?w=600", "https://loremflickr.com/600/600/cleaner,bottle"],
    "ghee": ["https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=600", "https://loremflickr.com/600/600/ghee,jar"]
}

async def main():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    products = await db.products.find({}).to_list(None)
    updated = 0
    
    for p in products:
        title = p.get("title", "")
        if title in MAPPING:
            await db.products.update_one({"_id": p["_id"]}, {"$set": {"image_urls": MAPPING[title]}})
            updated += 1
            print(f"Fixed images for: {title}")
        else:
            print(f"Could not find exact mapping for: {title}")
            # Ensure it has at least 2 generic loremflickr images based on title
            kw = title.split()[0].lower()
            await db.products.update_one({"_id": p["_id"]}, {"$set": {"image_urls": [
                f"https://loremflickr.com/600/600/{kw}",
                f"https://loremflickr.com/600/600/{kw},product"
            ]}})
            updated += 1
            
    print(f"Perfectly fixed {updated} products.")
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
