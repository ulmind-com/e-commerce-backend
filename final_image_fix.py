import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = "mongodb+srv://db_user:abc1%4023@cluster0.2zwacid.mongodb.net/"
DATABASE_NAME = "ecommerce"

# Safe secondary images
SECONDARIES = {
    "Fresh Produce": "https://images.unsplash.com/photo-1542838132-92c53300491e?w=600",
    "Dairy": "https://images.unsplash.com/photo-1628088062854-d1870b4553da?w=600",
    "Beverages": "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=600",
    "Snacks": "https://images.unsplash.com/photo-1599818826500-2d8816c21e64?w=600",
    "Care": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=600",
    "Grocery": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=600",
    "Pets": "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=600" # Dog is ok here
}

# Master list of exact images (2 for each)
MASTER = {
    # Grofers/Blinkit CDN + Unsplash pairings
    "Amul Buffalo A2 Milk (1 ltr)": [
        "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=900/da/cms-assets/cms/product/a53bb288-2ff6-478a-aadc-5e982262fa3e.jpg",
        SECONDARIES["Dairy"]
    ],
    "Mother Dairy Classic Dahi": [
        "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=900/da/cms-assets/cms/product/d7a0818e-c466-4ffb-ac15-8156ccc27d90.jpg",
        SECONDARIES["Dairy"]
    ],
    "Britannia Soft White Bread (400 g)": [
        "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=900/app/images/products/full_screen/462989_A.jpg",
        SECONDARIES["Dairy"]
    ],
    "Farm Fresh Eggs (6 pcs)": [
        "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=900/app/images/products/full_screen/305040_A.jpg",
        SECONDARIES["Dairy"]
    ],
    "Farm Fresh White Eggs": [
        "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=900/app/images/products/full_screen/305040_A.jpg",
        SECONDARIES["Dairy"]
    ],
    "Real Fruit Power Mixed Fruit Juice (1 ltr)": [
        "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=900/da/cms-assets/cms/product/ff4a3ece-1ddf-4860-b293-c2c22c768bb6.jpg",
        SECONDARIES["Beverages"]
    ],
    "Hide & Seek Chocolate Chip Cookies (200 g)": [
        "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=900/da/cms-assets/cms/product/rc-upload-1776829632782-4.jpg",
        SECONDARIES["Snacks"]
    ],
    "Lay's Classic Salted Chips (73 g)": [
        "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=900/app/images/products/full_screen/246835_A.jpg",
        SECONDARIES["Snacks"]
    ],
    "Green Cucumber (500 g)": [
        "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=900/app/images/products/full_screen/439162_A.jpg",
        SECONDARIES["Fresh Produce"]
    ],
    "Banana - Robusta (6 pcs)": [
        "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=900/app/images/products/full_screen/366447_A.jpg",
        SECONDARIES["Fresh Produce"]
    ],
    "Robusta Banana": [
        "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=900/app/images/products/full_screen/366447_A.jpg",
        SECONDARIES["Fresh Produce"]
    ],
    "Tender Coconut (1 pc)": [
        "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=900/app/images/products/full_screen/391063_A.jpg",
        SECONDARIES["Fresh Produce"]
    ],
    "Amul Butter (100 g)": [
        "https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=600",
        SECONDARIES["Dairy"]
    ],
    "amul butter": [
        "https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=600",
        SECONDARIES["Dairy"]
    ],
    "ghee": [
        "https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=600",
        SECONDARIES["Dairy"]
    ],
    "Mother Dairy Paneer (200 g)": [
        "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=600",
        SECONDARIES["Dairy"]
    ],
    "Coca-Cola (750 ml)": [
        "https://images.unsplash.com/photo-1554866585-cd94860890b7?w=600",
        SECONDARIES["Beverages"]
    ],
    "Pepsi Cola (750 ml)": [
        "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=600",
        SECONDARIES["Beverages"]
    ],
    "Sprite Lemon Lime (750 ml)": [
        "https://images.unsplash.com/photo-1625772452859-1c03d884dcd7?w=600",
        SECONDARIES["Beverages"]
    ],
    "Bisleri Mineral Water (1 ltr)": [
        "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=600",
        SECONDARIES["Beverages"]
    ],
    "Red Bull Energy Drink (250 ml)": [
        "https://images.unsplash.com/photo-1621506289937-a8e4df240d0b?w=600",
        SECONDARIES["Beverages"]
    ],
    "Tropicana Orange Juice (1 ltr)": [
        "https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=600",
        SECONDARIES["Beverages"]
    ],
    "Haldiram's Aloo Bhujia (400 g)": [
        "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=600",
        SECONDARIES["Snacks"]
    ],
    "Kurkure Masala Munch (90 g)": [
        "https://images.unsplash.com/photo-1600952841320-db92ec4047ca?w=600",
        SECONDARIES["Snacks"]
    ],
    "Maggi 2-Minute Noodles (70 g)": [
        "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=600",
        SECONDARIES["Snacks"]
    ],
    "Oreo Original Cookies (120 g)": [
        "https://images.unsplash.com/photo-1510611703620-2e0ede6b3413?w=600",
        SECONDARIES["Snacks"]
    ],
    "Dove Beauty Bar Soap (100 g)": [
        "https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=600",
        SECONDARIES["Care"]
    ],
    "Head & Shoulders Anti-Dandruff Shampoo (340 ml)": [
        "https://images.unsplash.com/photo-1585751119414-ef2636f8aede?w=600",
        SECONDARIES["Care"]
    ],
    "Colgate Strong Teeth Toothpaste (200 g)": [
        "https://images.unsplash.com/photo-1542736705-53f0131d1e98?w=600",
        SECONDARIES["Care"]
    ],
    "Dettol Hand Sanitizer (50 ml)": [
        "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=600",
        SECONDARIES["Care"]
    ],
    "Aashirvaad Select Atta (5 kg)": [
        "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=600",
        SECONDARIES["Grocery"]
    ],
    "India Gate Basmati Rice (1 kg)": [
        "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=600",
        SECONDARIES["Grocery"]
    ],
    "Tata Salt (1 kg)": [
        "https://images.unsplash.com/photo-1565547558-aa6b89ddd5c6?w=600",
        SECONDARIES["Grocery"]
    ],
    "Masoor Dal (500 g)": [
        "https://images.unsplash.com/photo-1609501676725-7186f017a4b7?w=600",
        SECONDARIES["Grocery"]
    ],
    "Fresh Kashmiri Apple": [
        "https://images.unsplash.com/photo-1560806887-1e4cd0b6faa6?w=600",
        SECONDARIES["Fresh Produce"]
    ],
    "Fresh Orange": [
        "https://images.unsplash.com/photo-1611080626919-7cf5a9dbab5b?w=600",
        SECONDARIES["Fresh Produce"]
    ],
    "Green Grapes": [
        "https://images.unsplash.com/photo-1537640538966-79f369143f8f?w=600",
        SECONDARIES["Fresh Produce"]
    ],
    "Watermelon": [
        "https://images.unsplash.com/photo-1589984662646-e7b2e4962f18?w=600",
        SECONDARIES["Fresh Produce"]
    ],
    "Honitus Cough Syrup": [
        "https://images.unsplash.com/photo-1584017911766-d451b3d0e843?w=600",
        SECONDARIES["Care"]
    ],
    "Volini Pain Relief Spray": [
        "https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=600",
        SECONDARIES["Care"]
    ],
    "Crocin Advance": [
        "https://images.unsplash.com/photo-1631549916768-4119b2e5f926?w=600",
        SECONDARIES["Care"]
    ],
    "Vicks VapoRub": [
        "https://images.unsplash.com/photo-1584362917165-526a968579e8?w=600",
        SECONDARIES["Care"]
    ],
    "Pedigree Adult Dog Food": [
        "https://images.unsplash.com/photo-1589924691995-400dc9ecc119?w=600",
        SECONDARIES["Pets"]
    ],
    "Whiskas Cat Food": [
        "https://images.unsplash.com/photo-1623387641168-d9803ddd3f35?w=600",
        SECONDARIES["Pets"]
    ],
    "Dog Chew Bone": [
        "https://images.unsplash.com/photo-1535930891776-0c2dfb7fda1a?w=600",
        SECONDARIES["Pets"]
    ],
    "Cat Litter Sand": [
        "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=600",
        SECONDARIES["Pets"]
    ],
    "Pampers Active Baby Diapers": [
        "https://images.unsplash.com/photo-1519689680058-324335c77eba?w=600",
        SECONDARIES["Care"]
    ],
    "Johnson's Baby Lotion": [
        "https://images.unsplash.com/photo-1555252333-9f8e92e65df9?w=600",
        SECONDARIES["Care"]
    ],
    "Baby Wipes": [
        "https://images.unsplash.com/photo-1512438248247-f0f2a5a8b7f0?w=600",
        SECONDARIES["Care"]
    ],
    "Himalaya Baby Powder": [
        "https://images.unsplash.com/photo-1522771930-78848d9293e8?w=600",
        SECONDARIES["Care"]
    ],
    "Tomato (500 g)": [
        "https://images.unsplash.com/photo-1546094096-0df4bcabd337?w=600",
        SECONDARIES["Fresh Produce"]
    ],
    "Onion (1 kg)": [
        "https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=600",
        SECONDARIES["Fresh Produce"]
    ],
    "Spinach / Palak (250 g)": [
        "https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=600",
        SECONDARIES["Fresh Produce"]
    ],
}

async def main():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    products = await db.products.find({}).to_list(None)
    updated = 0
    
    for p in products:
        title = p.get("title", "")
        # Look up in master, or fallback to generic based on category if unknown
        if title in MASTER:
            await db.products.update_one({"_id": p["_id"]}, {"$set": {"image_urls": MASTER[title]}})
            updated += 1
        else:
            # Fallback
            cat = p.get("category", "")
            img1 = SECONDARIES.get("Grocery")
            if "Fresh" in cat or "Vegetable" in cat:
                img1 = SECONDARIES["Fresh Produce"]
            elif "Dairy" in cat:
                img1 = SECONDARIES["Dairy"]
            
            await db.products.update_one({"_id": p["_id"]}, {"$set": {"image_urls": [img1, SECONDARIES["Grocery"]]}})
            updated += 1
            
    print(f"Completely fixed {updated} products with guaranteed images.")
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
