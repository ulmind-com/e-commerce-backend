import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

MONGODB_URL = "mongodb+srv://db_user:abc1%4023@cluster0.2zwacid.mongodb.net/"
DATABASE_NAME = "ecommerce"

CLOUDINARY_BASE = "https://res.cloudinary.com/dgkpawvia/image/upload/ecommerce/products"

# Category → slug mapping
CATEGORIES = [
    {"name": "Fresh Produce",     "slug": "fresh-produce",   "description": "Farm-fresh vegetables and fruits"},
    {"name": "Dairy & Bakery",    "slug": "dairy-bakery",    "description": "Fresh dairy, breads and eggs"},
    {"name": "Beverages",         "slug": "beverages",       "description": "Juices, sodas, water and more"},
    {"name": "Snacks",            "slug": "snacks",          "description": "Chips, cookies, namkeen and more"},
    {"name": "Personal Care",     "slug": "personal-care",   "description": "Skincare, hygiene and wellness"},
    {"name": "Staples & Grocery", "slug": "staples-grocery", "description": "Rice, dal, atta, spices and essentials"},
]

PRODUCTS = [
    # ── Fresh Produce ────────────────────────────────────────────────────────
    {"title": "Green Cucumber (500 g)", "description": "Fresh, crunchy cucumbers. Perfect for salads, raita, and healthy snacking.", "price": 25.0, "stock_quantity": 60, "category": "Fresh Produce",
     "image_urls": ["https://res.cloudinary.com/dgkpawvia/image/upload/v1781859599/ecommerce/products/green-cucumber.jpg"]},
    {"title": "Banana - Robusta (6 pcs)", "description": "Sweet, ripe Robusta bananas — a natural energy booster anytime.", "price": 35.0, "stock_quantity": 70, "category": "Fresh Produce",
     "image_urls": ["https://res.cloudinary.com/dgkpawvia/image/upload/v1781859600/ecommerce/products/fresh-banana.jpg"]},
    {"title": "Tender Coconut (1 pc)", "description": "Fresh tender coconut full of natural, hydrating coconut water.", "price": 55.0, "stock_quantity": 30, "category": "Fresh Produce",
     "image_urls": ["https://res.cloudinary.com/dgkpawvia/image/upload/v1781859601/ecommerce/products/tender-coconut.jpg"]},
    {"title": "Tomato (500 g)", "description": "Firm, ripe red tomatoes. Essential for curries, salads and gravies.", "price": 30.0, "stock_quantity": 80, "category": "Fresh Produce",
     "image_urls": ["https://images.unsplash.com/photo-1546094096-0df4bcabd337?w=400&q=80"]},
    {"title": "Onion (1 kg)", "description": "Farm-fresh onions. A kitchen essential for every Indian meal.", "price": 40.0, "stock_quantity": 100, "category": "Fresh Produce",
     "image_urls": ["https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=400&q=80"]},
    {"title": "Spinach / Palak (250 g)", "description": "Tender, fresh palak leaves. Great for dal palak, smoothies and stir-fry.", "price": 20.0, "stock_quantity": 50, "category": "Fresh Produce",
     "image_urls": ["https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=400&q=80"]},

    # ── Dairy & Bakery ───────────────────────────────────────────────────────
    {"title": "Amul Buffalo A2 Milk (1 ltr)", "description": "Rich, creamy A2 buffalo milk from Amul. Perfect for everyday use.", "price": 90.0, "stock_quantity": 50, "category": "Dairy & Bakery",
     "image_urls": ["https://res.cloudinary.com/dgkpawvia/image/upload/v1781859368/ecommerce/products/amul-buffalo-a2-milk.jpg"]},
    {"title": "Amul Masti Pouch Curd (400 g)", "description": "Thick and tasty curd, perfect for meals, raita, and lassi.", "price": 35.0, "stock_quantity": 100, "category": "Dairy & Bakery",
     "image_urls": ["https://res.cloudinary.com/dgkpawvia/image/upload/v1781859404/ecommerce/products/amul-masti-curd.jpg"]},
    {"title": "Britannia Soft White Bread (400 g)", "description": "Soft, fresh white sandwich bread. Perfect for breakfast and sandwiches.", "price": 40.0, "stock_quantity": 60, "category": "Dairy & Bakery",
     "image_urls": ["https://res.cloudinary.com/dgkpawvia/image/upload/v1781859595/ecommerce/products/britannia-white-bread.jpg"]},
    {"title": "Farm Fresh Eggs (6 pcs)", "description": "Fresh, protein-packed farm eggs — essential for every kitchen.", "price": 65.0, "stock_quantity": 80, "category": "Dairy & Bakery",
     "image_urls": ["https://res.cloudinary.com/dgkpawvia/image/upload/v1781859597/ecommerce/products/farm-fresh-eggs.jpg"]},
    {"title": "Amul Butter (100 g)", "description": "Delicious, creamy salted butter from Amul. Perfect on toast and for cooking.", "price": 55.0, "stock_quantity": 90, "category": "Dairy & Bakery",
     "image_urls": ["https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?w=400&q=80"]},
    {"title": "Mother Dairy Paneer (200 g)", "description": "Fresh, soft cottage cheese made from full-cream milk.", "price": 85.0, "stock_quantity": 40, "category": "Dairy & Bakery",
     "image_urls": ["https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=400&q=80"]},

    # ── Beverages ────────────────────────────────────────────────────────────
    {"title": "Coca-Cola (750 ml)", "description": "The refreshing taste of the world's most loved cola. Ice cold and fizzy.", "price": 45.0, "stock_quantity": 150, "category": "Beverages",
     "image_urls": ["https://images.unsplash.com/photo-1554866585-cd94860890b7?w=400&q=80"]},
    {"title": "Pepsi Cola (750 ml)", "description": "Bold, refreshing cola with the iconic Pepsi taste. Perfect for every occasion.", "price": 42.0, "stock_quantity": 150, "category": "Beverages",
     "image_urls": ["https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=400&q=80"]},
    {"title": "Sprite Lemon Lime (750 ml)", "description": "Crisp, clean lemon-lime flavour. The ultimate thirst quencher.", "price": 42.0, "stock_quantity": 120, "category": "Beverages",
     "image_urls": ["https://images.unsplash.com/photo-1625772452859-1c03d884dcd7?w=400&q=80"]},
    {"title": "Real Fruit Power Mixed Fruit Juice (1 ltr)", "description": "Refreshing mixed fruit juice made with real fruit. No added preservatives.", "price": 103.0, "stock_quantity": 40, "category": "Beverages",
     "image_urls": ["https://res.cloudinary.com/dgkpawvia/image/upload/v1781859407/ecommerce/products/real-fruit-juice.jpg"]},
    {"title": "Bisleri Mineral Water (1 ltr)", "description": "Pure, safe drinking water. Trusted by millions across India.", "price": 20.0, "stock_quantity": 200, "category": "Beverages",
     "image_urls": ["https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=400&q=80"]},
    {"title": "Red Bull Energy Drink (250 ml)", "description": "Vitalizes body and mind. Contains caffeine, taurine and B-group vitamins.", "price": 125.0, "stock_quantity": 60, "category": "Beverages",
     "image_urls": ["https://images.unsplash.com/photo-1621506289937-a8e4df240d0b?w=400&q=80"]},
    {"title": "Tropicana Orange Juice (1 ltr)", "description": "100% pure orange juice, made from hand-picked oranges. No added sugar.", "price": 120.0, "stock_quantity": 55, "category": "Beverages",
     "image_urls": ["https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=400&q=80"]},

    # ── Snacks ───────────────────────────────────────────────────────────────
    {"title": "Lay's Classic Salted Chips (73 g)", "description": "Light, crispy, perfectly salted potato chips — the original snack.", "price": 30.0, "stock_quantity": 120, "category": "Snacks",
     "image_urls": ["https://res.cloudinary.com/dgkpawvia/image/upload/v1781859598/ecommerce/products/lays-chips.jpg"]},
    {"title": "Hide & Seek Chocolate Chip Cookies (200 g)", "description": "Crunchy choco-chip cookies for your sweet cravings. Great with milk or tea.", "price": 48.0, "stock_quantity": 80, "category": "Snacks",
     "image_urls": ["https://res.cloudinary.com/dgkpawvia/image/upload/v1781859409/ecommerce/products/hide-seek-cookies.jpg"]},
    {"title": "Haldiram's Aloo Bhujia (400 g)", "description": "Crispy, spicy potato bhujia. A classic Indian snack loved across generations.", "price": 100.0, "stock_quantity": 90, "category": "Snacks",
     "image_urls": ["https://images.unsplash.com/photo-1601050690597-df0568f70950?w=400&q=80"]},
    {"title": "Kurkure Masala Munch (90 g)", "description": "Tangy and crunchy corn puffs with an irresistible masala flavour.", "price": 20.0, "stock_quantity": 150, "category": "Snacks",
     "image_urls": ["https://images.unsplash.com/photo-1600952841320-db92ec4047ca?w=400&q=80"]},
    {"title": "Maggi 2-Minute Noodles (70 g)", "description": "India's favourite instant noodles. Ready in just 2 minutes with the iconic Masala tastemaker.", "price": 14.0, "stock_quantity": 200, "category": "Snacks",
     "image_urls": ["https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400&q=80"]},
    {"title": "Oreo Original Cookies (120 g)", "description": "The world's favourite sandwich cookie with creamy vanilla filling.", "price": 65.0, "stock_quantity": 100, "category": "Snacks",
     "image_urls": ["https://images.unsplash.com/photo-1510611703620-2e0ede6b3413?w=400&q=80"]},

    # ── Personal Care ─────────────────────────────────────────────────────────
    {"title": "Dove Beauty Bar Soap (100 g)", "description": "Gentle, moisturising beauty bar. 1/4 moisturising cream for softer skin.", "price": 58.0, "stock_quantity": 100, "category": "Personal Care",
     "image_urls": ["https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=400&q=80"]},
    {"title": "Head & Shoulders Anti-Dandruff Shampoo (340 ml)", "description": "Clinically proven to remove dandruff flakes in just one wash.", "price": 299.0, "stock_quantity": 60, "category": "Personal Care",
     "image_urls": ["https://images.unsplash.com/photo-1585751119414-ef2636f8aede?w=400&q=80"]},
    {"title": "Colgate Strong Teeth Toothpaste (200 g)", "description": "Strengthens 8 natural teeth benefits. India's most trusted toothpaste.", "price": 99.0, "stock_quantity": 80, "category": "Personal Care",
     "image_urls": ["https://images.unsplash.com/photo-1542736705-53f0131d1e98?w=400&q=80"]},
    {"title": "Dettol Hand Sanitizer (50 ml)", "description": "Kills 99.9% of germs without water. Convenient travel-size bottle.", "price": 79.0, "stock_quantity": 120, "category": "Personal Care",
     "image_urls": ["https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400&q=80"]},

    # ── Staples & Grocery ─────────────────────────────────────────────────────
    {"title": "Aashirvaad Select Atta (5 kg)", "description": "100% whole wheat atta. High protein content for soft, fluffy rotis every day.", "price": 265.0, "stock_quantity": 50, "category": "Staples & Grocery",
     "image_urls": ["https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=400&q=80"]},
    {"title": "India Gate Basmati Rice (1 kg)", "description": "Long grain, aromatic basmati rice. Perfect for biryani and pulao.", "price": 130.0, "stock_quantity": 60, "category": "Staples & Grocery",
     "image_urls": ["https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400&q=80"]},
    {"title": "Tata Salt (1 kg)", "description": "Pure iodised salt from Tata. India's most trusted kitchen essential.", "price": 25.0, "stock_quantity": 200, "category": "Staples & Grocery",
     "image_urls": ["https://images.unsplash.com/photo-1565547558-aa6b89ddd5c6?w=400&q=80"]},
    {"title": "Masoor Dal (500 g)", "description": "Premium quality red lentils. Easy to cook, high in protein and iron.", "price": 75.0, "stock_quantity": 80, "category": "Staples & Grocery",
     "image_urls": ["https://images.unsplash.com/photo-1609501676725-7186f017a4b7?w=400&q=80"]},
]


async def seed_database():
    print("Connecting to MongoDB Atlas...")
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]

    print("Clearing existing data...")
    await db.categories.delete_many({})
    await db.products.delete_many({})

    # Insert categories
    print(f"Inserting {len(CATEGORIES)} categories...")
    cat_result = await db.categories.insert_many(
        [{**c, "is_active": True, "created_at": datetime.utcnow()} for c in CATEGORIES]
    )
    cat_id_map = {
        cat["name"]: str(inserted_id)
        for cat, inserted_id in zip(CATEGORIES, cat_result.inserted_ids)
    }
    print("Categories:", list(cat_id_map.keys()))

    # Insert products
    print(f"Inserting {len(PRODUCTS)} products...")
    products_to_insert = []
    for p in PRODUCTS:
        cat_name = p.pop("category")
        products_to_insert.append({
            **p,
            "category_id": cat_id_map.get(cat_name, ""),
            "is_published": True,
            "created_at": datetime.utcnow(),
        })
    await db.products.insert_many(products_to_insert)

    print(f"\n✅ Seeded {len(CATEGORIES)} categories and {len(PRODUCTS)} products!")
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_database())
