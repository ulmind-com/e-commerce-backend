import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import requests
import urllib.parse
import time

MONGODB_URL = "mongodb+srv://db_user:abc1%4023@cluster0.2zwacid.mongodb.net/"
DATABASE_NAME = "ecommerce"

def search_wikimedia(query):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(query)}&gsrnamespace=6&gsrlimit=2&prop=imageinfo&iiprop=url&format=json"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers)
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

MAPPING = {
    "Mr. Merchant Paan Shots": "Paan",
    "Tiny Mint Saunf": "Fennel seeds",
    "Imli Ladoo Churan Candy": "Tamarind",
    "Sugar Coated Saunf": "Fennel seeds",
    "Supply6 Salts Lime Electrolyte Mix": "Sports drink",
    "Kombucha Hibiscus Lime": "Kombucha",
    "Kombucha Blueberry Lavender": "Kombucha",
    "Krishna's Herbal & Ayurveda Aloe Vera": "Aloe vera juice",
    "Kombucha Original": "Kombucha",
    "Aam Papad Mukwas": "Mango candy",
    "Nature's Trunk Ginger Digestive Candy": "Ginger candy",
    "Hexhive Honey Ginger Digestives": "Ginger candy",
    "Swad Aam Papad Candy": "Mango candy",
    "Amul Taaza Toned Fresh Milk": "Milk glass",
    "Farm Fresh White Eggs": "White eggs",
    "Harvest Gold White Bread": "White bread",
    "Mother Dairy Classic Dahi": "Yogurt bowl",
    "Fresh Kashmiri Apple": "Red apple",
    "Robusta Banana": "Banana bunch",
    "Fresh Orange": "Orange fruit",
    "Green Grapes": "Green grapes",
    "Watermelon": "Watermelon slice",
    "Honitus Cough Syrup": "Cough syrup",
    "Volini Pain Relief Spray": "Pain relief spray",
    "Crocin Advance": "Paracetamol pills",
    "Vicks VapoRub": "Vicks VapoRub",
    "Pedigree Adult Dog Food": "Dog food bowl",
    "Whiskas Cat Food": "Cat food bowl",
    "Dog Chew Bone": "Dog chew bone",
    "Cat Litter Sand": "Cat litter",
    "Pampers Active Baby Diapers": "Baby diapers",
    "Johnson's Baby Lotion": "Baby lotion",
    "Baby Wipes": "Baby wipes",
    "Himalaya Baby Powder": "Baby powder",
    "amul butter": "Amul butter",
    "lizol": "Floor cleaner bottle",
    "ghee": "Ghee jar"
}

async def main():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    products = await db.products.find({}).to_list(None)
    for p in products:
        title = p["title"]
        search_term = MAPPING.get(title)
        if search_term:
            urls = search_wikimedia(search_term)
            if len(urls) == 0:
                # fallback to just searching the title
                urls = search_wikimedia(title)
            
            # If still nothing, fallback to generic
            if len(urls) == 0:
                urls = ["https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/600px-No_image_available.svg.png", 
                        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/600px-No_image_available.svg.png"]
            elif len(urls) == 1:
                urls.append(urls[0])
                
            print(f"Updating {title} with {urls}")
            await db.products.update_one({"_id": p["_id"]}, {"$set": {"image_urls": urls}})
            time.sleep(0.5) # rate limit protection
    print("Done updating images via Wikimedia Commons!")
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
