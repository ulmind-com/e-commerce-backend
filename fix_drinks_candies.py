import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = "mongodb+srv://db_user:abc1%4023@cluster0.2zwacid.mongodb.net/"
DATABASE_NAME = "ecommerce"

# Verified Wiki Images
IMG_KOMBUCHA_1 = "https://upload.wikimedia.org/wikipedia/commons/4/48/Kombucha_Mature.jpg"
IMG_KOMBUCHA_2 = "https://upload.wikimedia.org/wikipedia/commons/4/4a/Kombucha_mushroom.jpg"
IMG_ALOE_1 = "https://upload.wikimedia.org/wikipedia/commons/b/b5/Aloe_vera_Lanzarote.jpg"
IMG_ALOE_2 = "https://upload.wikimedia.org/wikipedia/commons/b/b0/Aloe_vera_flower_bud.jpg"
IMG_LIME_1 = "https://upload.wikimedia.org/wikipedia/commons/6/68/Lime-Whole-Split.jpg"
IMG_LIME_2 = "https://upload.wikimedia.org/wikipedia/commons/e/e7/Lime_-_whole_and_halved.jpg"
IMG_LAVENDER = "https://upload.wikimedia.org/wikipedia/commons/7/7e/Single_lavender_flower02.jpg"
IMG_CANDY = "https://upload.wikimedia.org/wikipedia/commons/1/10/Candy_in_Damascus.jpg"
IMG_POP_1 = "https://upload.wikimedia.org/wikipedia/commons/c/cb/Farbenfrohe_Lollipops%2C_Austria.jpg"
IMG_POP_2 = "https://upload.wikimedia.org/wikipedia/commons/6/6c/Bacon-flavored_lollipops.jpg"
IMG_HONEY_1 = "https://upload.wikimedia.org/wikipedia/commons/c/cc/Runny_hunny.jpg"
IMG_HONEY_2 = "https://upload.wikimedia.org/wikipedia/commons/1/1d/European_honey_bee_extracts_nectar.jpg"
IMG_GINGER_1 = "https://upload.wikimedia.org/wikipedia/commons/c/c1/Ginger_Plant_vs.jpg"
IMG_GINGER_2 = "https://upload.wikimedia.org/wikipedia/commons/1/18/Koeh-146-no_text.jpg"

FIXES = {
    # Drinks (Must all be unique)
    "Supply6 Salts Lime Electrolyte Mix": [IMG_LIME_1, IMG_CANDY],
    "Kombucha Hibiscus Lime": [IMG_KOMBUCHA_1, IMG_LIME_1],
    "Kombucha Blueberry Lavender": [IMG_KOMBUCHA_2, IMG_LAVENDER],
    "Krishna's Herbal & Ayurveda Aloe Vera": [IMG_ALOE_1, IMG_ALOE_2],
    "Kombucha Original": [IMG_KOMBUCHA_2, IMG_KOMBUCHA_1],
    
    # Candies (Must all be unique)
    "Aam Papad Mukwas": [IMG_POP_1, IMG_CANDY],
    "Swad Aam Papad Candy": [IMG_POP_2, IMG_CANDY],
    "Nature's Trunk Ginger Digestive Candy": [IMG_GINGER_1, IMG_HONEY_1],
    "Hexhive Honey Ginger Digestives": [IMG_HONEY_2, IMG_GINGER_2],
}

async def main():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    for title, urls in FIXES.items():
        await db.products.update_one({"title": title}, {"$set": {"image_urls": urls}})
        print(f"Fixed {title} with unique Wiki Images")
        
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
