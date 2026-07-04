import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = "mongodb+srv://db_user:abc1%4023@cluster0.2zwacid.mongodb.net/"
DATABASE_NAME = "ecommerce"

MAPPING = {
  "Mr. Merchant Paan Shots": ["https://images.unsplash.com/photo-1615598688402-316238da56bd?w=600", "https://images.unsplash.com/photo-1596728004547-49db0189a421?w=600"],
  "Tiny Mint Saunf": ["https://images.unsplash.com/photo-1615598688402-316238da56bd?w=600", "https://images.unsplash.com/photo-1621506289937-a8e4df240d0b?w=600"],
  "Imli Ladoo Churan Candy": ["https://images.unsplash.com/photo-1582050041567-9cfec355c9ee?w=600", "https://images.unsplash.com/photo-1517260739337-6799d239ce83?w=600"],
  "Sugar Coated Saunf": ["https://images.unsplash.com/photo-1574316071802-0d684efa7ea5?w=600", "https://images.unsplash.com/photo-1596728004547-49db0189a421?w=600"],
  "Supply6 Salts Lime Electrolyte Mix": ["https://images.unsplash.com/photo-1551538827-9c037cb4f32a?w=600", "https://images.unsplash.com/photo-1527661591475-527312dd65f5?w=600"],
  "Kombucha Hibiscus Lime": ["https://images.unsplash.com/photo-1595981267035-7b04d84b4f1e?w=600", "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=600"],
  "Kombucha Blueberry Lavender": ["https://images.unsplash.com/photo-1551538827-9c037cb4f32a?w=600", "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=600"],
  "Krishna's Herbal & Ayurveda Aloe Vera": ["https://images.unsplash.com/photo-1596547609652-9fc5b8ce3660?w=600", "https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=600"],
  "Kombucha Original": ["https://images.unsplash.com/photo-1595981267035-7b04d84b4f1e?w=600", "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=600"],
  "Aam Papad Mukwas": ["https://images.unsplash.com/photo-1621506289937-a8e4df240d0b?w=600", "https://images.unsplash.com/photo-1582050041567-9cfec355c9ee?w=600"],
  "Nature's Trunk Ginger Digestive Candy": ["https://images.unsplash.com/photo-1599818826500-2d8816c21e64?w=600", "https://images.unsplash.com/photo-1582050041567-9cfec355c9ee?w=600"],
  "Hexhive Honey Ginger Digestives": ["https://images.unsplash.com/photo-1587049352847-4d45d8b87ee8?w=600", "https://images.unsplash.com/photo-1599818826500-2d8816c21e64?w=600"],
  "Swad Aam Papad Candy": ["https://images.unsplash.com/photo-1582050041567-9cfec355c9ee?w=600", "https://images.unsplash.com/photo-1517260739337-6799d239ce83?w=600"],
  "Amul Taaza Toned Fresh Milk": ["https://images.unsplash.com/photo-1550583724-b2692b85b150?w=600", "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=600"],
  "Farm Fresh White Eggs": ["https://images.unsplash.com/photo-1587486913049-53fc88980cb5?w=600", "https://images.unsplash.com/photo-1506976785307-8732e854ad03?w=600"],
  "Harvest Gold White Bread": ["https://images.unsplash.com/photo-1598373182133-52452f7691ef?w=600", "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=600"],
  "Mother Dairy Classic Dahi": ["https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=600", "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=600"],
  "Fresh Kashmiri Apple": ["https://images.unsplash.com/photo-1560806887-1e4cd0b6faa6?w=600", "https://images.unsplash.com/photo-1579613832125-5d34a13ffe2a?w=600"],
  "Robusta Banana": ["https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=600", "https://images.unsplash.com/photo-1603833665858-e61d17a86224?w=600"],
  "Fresh Orange": ["https://images.unsplash.com/photo-1547514701-42782101795e?w=600", "https://images.unsplash.com/photo-1582979512210-99b6a53386f9?w=600"],
  "Green Grapes": ["https://images.unsplash.com/photo-1537640538966-79f369143f8f?w=600", "https://images.unsplash.com/photo-1596368708356-6e1e1025ee72?w=600"],
  "Watermelon": ["https://images.unsplash.com/photo-1587049352847-4d45d8b87ee8?w=600", "https://images.unsplash.com/photo-1589984662646-e7b2e4962f18?w=600"],
  "Honitus Cough Syrup": ["https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=600", "https://images.unsplash.com/photo-1584017911766-d451b3d0e843?w=600"],
  "Volini Pain Relief Spray": ["https://images.unsplash.com/photo-1583947215259-38e31be8751f?w=600", "https://images.unsplash.com/photo-1550572017-edb7305928f1?w=600"],
  "Crocin Advance": ["https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=600", "https://images.unsplash.com/photo-1550572017-edb7305928f1?w=600"],
  "Vicks VapoRub": ["https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=600", "https://images.unsplash.com/photo-1550572017-edb7305928f1?w=600"],
  "Pedigree Adult Dog Food": ["https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=600", "https://images.unsplash.com/photo-1589923188900-85dae523342b?w=600"],
  "Whiskas Cat Food": ["https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=600", "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=600"],
  "Dog Chew Bone": ["https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=600", "https://images.unsplash.com/photo-1589923188900-85dae523342b?w=600"],
  "Cat Litter Sand": ["https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=600", "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=600"],
  "Pampers Active Baby Diapers": ["https://images.unsplash.com/photo-1555252136-1e6d4c6731be?w=600", "https://images.unsplash.com/photo-1544642899-f0d6e5f6ed6f?w=600"],
  "Johnson's Baby Lotion": ["https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=600", "https://images.unsplash.com/photo-1555252136-1e6d4c6731be?w=600"],
  "Baby Wipes": ["https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=600", "https://images.unsplash.com/photo-1555252136-1e6d4c6731be?w=600"],
  "Himalaya Baby Powder": ["https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=600", "https://images.unsplash.com/photo-1555252136-1e6d4c6731be?w=600"],
  "amul butter": ["https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=600", "https://images.unsplash.com/photo-1626079450379-66c3a37b3fbd?w=600"],
  "lizol": ["https://images.unsplash.com/photo-1584820927508-0118357eb482?w=600", "https://images.unsplash.com/photo-1585836894082-96426477e382?w=600"],
  "ghee": ["https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=600", "https://images.unsplash.com/photo-1626079450379-66c3a37b3fbd?w=600"],
}

async def main():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    products = await db.products.find({}).to_list(None)
    updated = 0
    
    for p in products:
        title = p.get("title", "")
        images = p.get("image_urls", [])
        
        if title in MAPPING:
            # We want to append to the FIRST original image
            new_images = [images[0]] if images else []
            for img in MAPPING[title]:
                if img not in new_images:
                    new_images.append(img)
            
            await db.products.update_one({"_id": p["_id"]}, {"$set": {"image_urls": new_images}})
            updated += 1
            
    print(f"Added exact relevant images for {updated} products.")
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
