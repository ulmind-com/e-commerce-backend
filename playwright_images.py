import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from playwright.async_api import async_playwright
import urllib.parse
import json

MONGODB_URL = "mongodb+srv://db_user:abc1%4023@cluster0.2zwacid.mongodb.net/"
DATABASE_NAME = "ecommerce"

async def main():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    products = await db.products.find({}).to_list(None)
    
    print(f"Starting Google Image search for {len(products)} products...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Randomize user agent slightly
        page = await browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")
        
        for p in products:
            title = p.get("title", "")
            if not title:
                continue
                
            query = f"{title} product packaging india"
            url = f"https://www.google.com/search?tbm=isch&q={urllib.parse.quote(query)}"
            
            try:
                await page.goto(url, wait_until="domcontentloaded")
                await page.wait_for_timeout(1000) # give images time to load
                
                # Extract image src from img tags
                imgs = await page.evaluate('''() => {
                    const images = Array.from(document.querySelectorAll('img'));
                    return images
                        .map(img => img.src)
                        .filter(src => src && (src.startsWith('http') || src.startsWith('data:image')))
                        .slice(1, 4); // skip first (google logo)
                }''')
                
                # Get first 2 images
                if len(imgs) >= 2:
                    final_urls = imgs[:2]
                elif len(imgs) == 1:
                    final_urls = [imgs[0], imgs[0]]
                else:
                    final_urls = []
                    
                if final_urls:
                    await db.products.update_one({"_id": p["_id"]}, {"$set": {"image_urls": final_urls}})
                    print(f"[OK] Updated {title} with {len(final_urls)} images.")
                else:
                    print(f"[FAIL] No images found for {title}")
                    
            except Exception as e:
                print(f"[ERROR] Failed {title}: {e}")
                
        await browser.close()
    
    client.close()
    print("Finished updating all products with Google Images!")

if __name__ == "__main__":
    asyncio.run(main())
