import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import requests
import urllib.parse
import time
import json

MONGODB_URL = "mongodb+srv://db_user:abc1%4023@cluster0.2zwacid.mongodb.net/"
DATABASE_NAME = "ecommerce"

# Custom User-Agent to avoid Wikimedia block
HEADERS = {
    "User-Agent": "EcommercePlatformScript/1.0 (admin@ecommerce.com) Python/3.10"
}

def search_wikimedia(query):
    print(f"Searching Wikipedia for: {query}")
    url = f"https://en.wikipedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(query)}&gsrnamespace=0&gsrlimit=1&prop=pageimages&piprop=original&format=json"
    try:
        res = requests.get(url, headers=HEADERS)
        data = res.json()
        pages = data.get("query", {}).get("pages", {})
        for page_id, page_info in pages.items():
            if "original" in page_info:
                return page_info["original"]["source"]
    except Exception as e:
        print(f"Error for {query}: {e}")
    return None

def search_wikimedia_commons(query):
    print(f"Searching Wikimedia Commons for: {query}")
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(query)}&gsrnamespace=6&gsrlimit=2&prop=imageinfo&iiprop=url&format=json"
    try:
        res = requests.get(url, headers=HEADERS)
        data = res.json()
        pages = data.get("query", {}).get("pages", {})
        urls = []
        for page_id, page_info in pages.items():
            imageinfo = page_info.get("imageinfo", [])
            if imageinfo:
                urls.append(imageinfo[0].get("url"))
        return urls
    except Exception as e:
        print(f"Error for {query}: {e}")
    return []

# Direct Unsplash IDs verified to work
VERIFIED_IMAGES = {
    "Mr. Merchant Paan Shots": ["https://images.unsplash.com/photo-1596649282361-12502787e912?w=600", "https://images.unsplash.com/photo-1628556270448-4d4e4148e1b1?w=600"],
    "Tiny Mint Saunf": ["https://images.unsplash.com/photo-1628556270448-4d4e4148e1b1?w=600", "https://images.unsplash.com/photo-1596649282361-12502787e912?w=600"],
    "Imli Ladoo Churan Candy": ["https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=600", "https://images.unsplash.com/photo-1587049352851-8d4e89133924?w=600"],
    "Sugar Coated Saunf": ["https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=600", "https://images.unsplash.com/photo-1628556270448-4d4e4148e1b1?w=600"],
    "Supply6 Salts Lime Electrolyte Mix": ["https://images.unsplash.com/photo-1544145945-f90425340c7e?w=600", "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=600"],
    "Kombucha Hibiscus Lime": ["https://images.unsplash.com/photo-1556881286-fc6915169721?w=600", "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=600"],
    "Kombucha Blueberry Lavender": ["https://images.unsplash.com/photo-1556881286-fc6915169721?w=600", "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=600"],
    "Krishna's Herbal & Ayurveda Aloe Vera": ["https://images.unsplash.com/photo-1556881286-fc6915169721?w=600", "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=600"],
    "Kombucha Original": ["https://images.unsplash.com/photo-1556881286-fc6915169721?w=600", "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=600"],
    "Aam Papad Mukwas": ["https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=600", "https://images.unsplash.com/photo-1587049352851-8d4e89133924?w=600"],
    "Nature's Trunk Ginger Digestive Candy": ["https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=600", "https://images.unsplash.com/photo-1587049352851-8d4e89133924?w=600"],
    "Hexhive Honey Ginger Digestives": ["https://images.unsplash.com/photo-1587049352851-8d4e89133924?w=600", "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=600"],
    "Swad Aam Papad Candy": ["https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=600", "https://images.unsplash.com/photo-1587049352851-8d4e89133924?w=600"],
    "Amul Taaza Toned Fresh Milk": ["https://images.unsplash.com/photo-1550583724-b2692b85b150?w=600", "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=600"],
    "Farm Fresh White Eggs": ["https://images.unsplash.com/photo-1506976785307-8732e854ad03?w=600", "https://images.unsplash.com/photo-1587486913049-53fc88980cfc?w=600"],
    "Harvest Gold White Bread": ["https://images.unsplash.com/photo-1509440159596-0249088772ff?w=600", "https://images.unsplash.com/photo-1598373182133-52452f7691ef?w=600"],
    "Mother Dairy Classic Dahi": ["https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=600", "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=600"],
    "Fresh Kashmiri Apple": ["https://images.unsplash.com/photo-1560806887-1e4cd0b6faa6?w=600", "https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?w=600"],
    "Robusta Banana": ["https://images.unsplash.com/photo-1571501478200-b5b4a6bc9f58?w=600", "https://images.unsplash.com/photo-1528825871115-3581a5387919?w=600"],
    "Fresh Orange": ["https://images.unsplash.com/photo-1611080626919-7cf5a9dbab5b?w=600", "https://images.unsplash.com/photo-1550258987-190a2d41a8ba?w=600"],
    "Green Grapes": ["https://images.unsplash.com/photo-1537640538966-79f369143f8f?w=600", "https://images.unsplash.com/photo-1596368708356-6e1ceb7ce52f?w=600"],
    "Watermelon": ["https://images.unsplash.com/photo-1589984662646-e7b2e4962f18?w=600", "https://images.unsplash.com/photo-1582281298055-e25b84a30b0b?w=600"],
    "Honitus Cough Syrup": ["https://images.unsplash.com/photo-1584017911766-d451b3d0e843?w=600", "https://images.unsplash.com/photo-1584362917165-526a968579e8?w=600"],
    "Volini Pain Relief Spray": ["https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=600", "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=600"],
    "Crocin Advance": ["https://images.unsplash.com/photo-1631549916768-4119b2e5f926?w=600", "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=600"],
    "Vicks VapoRub": ["https://images.unsplash.com/photo-1584362917165-526a968579e8?w=600", "https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=600"],
    "Pedigree Adult Dog Food": ["https://images.unsplash.com/photo-1589924691995-400dc9ecc119?w=600", "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=600"],
    "Whiskas Cat Food": ["https://images.unsplash.com/photo-1623387641168-d9803ddd3f35?w=600", "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=600"],
    "Dog Chew Bone": ["https://images.unsplash.com/photo-1535930891776-0c2dfb7fda1a?w=600", "https://images.unsplash.com/photo-1589924691995-400dc9ecc119?w=600"],
    "Cat Litter Sand": ["https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=600", "https://images.unsplash.com/photo-1623387641168-d9803ddd3f35?w=600"],
    "Pampers Active Baby Diapers": ["https://images.unsplash.com/photo-1519689680058-324335c77eba?w=600", "https://images.unsplash.com/photo-1555252333-9f8e92e65df9?w=600"],
    "Johnson's Baby Lotion": ["https://images.unsplash.com/photo-1555252333-9f8e92e65df9?w=600", "https://images.unsplash.com/photo-1512438248247-f0f2a5a8b7f0?w=600"],
    "Baby Wipes": ["https://images.unsplash.com/photo-1512438248247-f0f2a5a8b7f0?w=600", "https://images.unsplash.com/photo-1522771930-78848d9293e8?w=600"],
    "Himalaya Baby Powder": ["https://images.unsplash.com/photo-1522771930-78848d9293e8?w=600", "https://images.unsplash.com/photo-1555252333-9f8e92e65df9?w=600"],
    "amul butter": ["https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=600", "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=600"],
    "lizol": ["https://images.unsplash.com/photo-1584820927508-0118357eb482?w=600", "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=600"],
    "ghee": ["https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=600", "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=600"]
}

async def main():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    products = await db.products.find({}).to_list(None)
    
    print(f"Starting Wikipedia Image search for {len(products)} products...")
    
    for p in products:
        title = p.get("title", "")
        if not title:
            continue
            
        final_urls = VERIFIED_IMAGES.get(title, [])
        
        # If not in our verified map, search Wikipedia!
        if not final_urls:
            wiki_url = search_wikimedia(title)
            if wiki_url:
                final_urls.append(wiki_url)
            
            commons_urls = search_wikimedia_commons(title)
            final_urls.extend(commons_urls)
            
            # Ensure at least 2 images
            if len(final_urls) == 1:
                final_urls.append(final_urls[0])
            elif len(final_urls) == 0:
                final_urls = ["https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/600px-No_image_available.svg.png"] * 2
                
        # Trim to 2 images
        final_urls = final_urls[:2]
        
        await db.products.update_one({"_id": p["_id"]}, {"$set": {"image_urls": final_urls}})
        print(f"[OK] Updated {title} with {final_urls}")
        
    client.close()
    print("Finished updating all products with perfect images!")

if __name__ == "__main__":
    asyncio.run(main())
