from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
import asyncio
from datetime import datetime

client = None
db = None
_use_fallback = False

class InMemoryCollection:
    """Simple in-memory collection that mimics basic MongoDB operations for local dev."""
    def __init__(self):
        self._docs = []

    async def find_one(self, filter_dict):
        for doc in self._docs:
            if all(doc.get(k) == v for k, v in filter_dict.items()):
                return doc
        return None

    async def count_documents(self, filter_dict):
        # Extremely simplified count for $gte etc.
        count = 0
        for doc in self._docs:
            match = True
            for k, v in filter_dict.items():
                if isinstance(v, dict) and "$gte" in v:
                    if doc.get(k) is None or doc.get(k) < v["$gte"]:
                        match = False
                elif doc.get(k) != v:
                    match = False
            if match:
                count += 1
        return count

    def find(self, filter_dict=None):
        if filter_dict is None:
            filter_dict = {}
        return InMemoryCursor([
            doc for doc in self._docs
            if all(doc.get(k) == v for k, v in filter_dict.items())
        ])

    async def insert_one(self, doc):
        self._docs.append(doc)
        return type('Result', (), {'inserted_id': doc.get('_id')})()

    async def update_one(self, filter_dict, update):
        for i, doc in enumerate(self._docs):
            if all(doc.get(k) == v for k, v in filter_dict.items()):
                if "$set" in update:
                    doc.update(update["$set"])
                if "$push" in update:
                    for key, val in update["$push"].items():
                        if key not in doc:
                            doc[key] = []
                        doc[key].append(val)
                return type('Result', (), {'modified_count': 1})()
        return type('Result', (), {'modified_count': 0})()

    async def find_one_and_update(self, filter_dict, update, return_document=False, **kwargs):
        for i, doc in enumerate(self._docs):
            if all(doc.get(k) == v for k, v in filter_dict.items()):
                original = doc.copy()
                if "$set" in update:
                    doc.update(update["$set"])
                if "$push" in update:
                    for key, val in update["$push"].items():
                        if key not in doc:
                            doc[key] = []
                        doc[key].append(val)
                return doc if return_document else original
        return None

    def aggregate(self, pipeline):
        if len(pipeline) >= 2 and "$match" in pipeline[0] and "$group" in pipeline[1]:
            match_date = pipeline[0]["$match"].get("created_at", {}).get("$gte")
            if match_date:
                total = sum(doc.get("total_amount", 0) for doc in self._docs if doc.get("created_at") and doc["created_at"] >= match_date)
                return InMemoryCursor([{"_id": None, "total": total}])
        return InMemoryCursor([])

    async def delete_one(self, filter_dict):
        for i, doc in enumerate(self._docs):
            if all(doc.get(k) == v for k, v in filter_dict.items()):
                self._docs.pop(i)
                return type('Result', (), {'deleted_count': 1})()
        return type('Result', (), {'deleted_count': 0})()

class InMemoryCursor:
    def __init__(self, docs):
        self._docs = docs
        self._skip = 0
        self._limit_val = None

    def skip(self, n):
        self._skip = n
        return self

    def sort(self, key_or_list, direction=None):
        try:
            if isinstance(key_or_list, str):
                key = key_or_list
                reverse = direction == -1
            else:
                key = key_or_list[0][0]
                reverse = key_or_list[0][1] == -1
            self._docs = sorted(self._docs, key=lambda d: d.get(key) if d.get(key) is not None else "", reverse=reverse)
        except Exception:
            pass
        return self

    def limit(self, n):
        self._limit_val = n
        return self

    async def to_list(self, length=None):
        docs = self._docs[self._skip:]
        limit = self._limit_val or length
        if limit:
            docs = docs[:limit]
        return docs

class InMemoryDB:
    """Simple in-memory database that mimics MongoDB database access."""
    def __init__(self):
        self._collections = {}
        # Pre-seed users, categories and products for local dev without MongoDB
        users = [
            {
                "_id": "admin_1",
                "email": "admin@onebasket.com",
                "full_name": "Admin User",
                "role": "admin",
                "hashed_password": "$2b$12$XLyloJ6.Iu5UtwKDUsK5du9x0VpKG2D2uub8rLAW2izjGaTJISOR.",
                "created_at": datetime.utcnow()
            }
        ]
        categories = [
            {"_id": "cat_1", "name": "Dairy, Bread & Eggs", "description": "Fresh dairy, breads and daily eggs", "slug": "dairy-bread-eggs"},
            {"_id": "cat_2", "name": "Snacks & Drinks", "description": "Munchies and refreshing beverages", "slug": "snacks-drinks"},
            {"_id": "cat_3", "name": "Vegetables & Fruits", "description": "Farm fresh veggies and fruits", "slug": "vegetables-fruits"}
        ]
        products = [
            {
                "_id": "prod_1",
                "title": "Amul Buffalo A2 Milk (1 ltr)",
                "description": "Rich, creamy, and nutritious A2 buffalo milk from Amul.",
                "price": 90.0, "stock_quantity": 50, "category_id": "cat_1", "is_published": True,
                "image_urls": ["https://res.cloudinary.com/dgkpawvia/image/upload/v1781859368/ecommerce/products/amul-buffalo-a2-milk.jpg"],
            },
            {
                "_id": "prod_2",
                "title": "Amul Masti Pouch Curd (400 g)",
                "description": "Thick and tasty curd, perfect for meals and raita.",
                "price": 35.0, "stock_quantity": 100, "category_id": "cat_1", "is_published": True,
                "image_urls": ["https://res.cloudinary.com/dgkpawvia/image/upload/v1781859404/ecommerce/products/amul-masti-curd.jpg"],
            },
            {
                "_id": "prod_3",
                "title": "Britannia Soft White Bread (400 g)",
                "description": "Soft, fresh white sandwich bread. Perfect for breakfast.",
                "price": 40.0, "stock_quantity": 60, "category_id": "cat_1", "is_published": True,
                "image_urls": ["https://res.cloudinary.com/dgkpawvia/image/upload/v1781859595/ecommerce/products/britannia-white-bread.jpg"],
            },
            {
                "_id": "prod_4",
                "title": "Farm Fresh Eggs (6 pcs)",
                "description": "Fresh, protein-packed farm eggs — essential for every kitchen.",
                "price": 65.0, "stock_quantity": 80, "category_id": "cat_1", "is_published": True,
                "image_urls": ["https://res.cloudinary.com/dgkpawvia/image/upload/v1781859597/ecommerce/products/farm-fresh-eggs.jpg"],
            },
            {
                "_id": "prod_5",
                "title": "Real Fruit Power Mixed Fruit Juice (1 ltr)",
                "description": "Refreshing mixed fruit juice with real fruit. No preservatives.",
                "price": 103.0, "stock_quantity": 40, "category_id": "cat_2", "is_published": True,
                "image_urls": ["https://res.cloudinary.com/dgkpawvia/image/upload/v1781859407/ecommerce/products/real-fruit-juice.jpg"],
            },
            {
                "_id": "prod_6",
                "title": "Hide & Seek Chocolate Chip Cookies (200 g)",
                "description": "Crunchy choco-chip cookies for your sweet cravings.",
                "price": 48.0, "stock_quantity": 80, "category_id": "cat_2", "is_published": True,
                "image_urls": ["https://res.cloudinary.com/dgkpawvia/image/upload/v1781859409/ecommerce/products/hide-seek-cookies.jpg"],
            },
            {
                "_id": "prod_7",
                "title": "Lay's Classic Salted Chips (73 g)",
                "description": "Light, crispy, and perfectly salted potato chips.",
                "price": 30.0, "stock_quantity": 120, "category_id": "cat_2", "is_published": True,
                "image_urls": ["https://res.cloudinary.com/dgkpawvia/image/upload/v1781859598/ecommerce/products/lays-chips.jpg"],
            },
            {
                "_id": "prod_8",
                "title": "Green Cucumber (500 g)",
                "description": "Fresh, crunchy cucumbers. Perfect for salads and raita.",
                "price": 25.0, "stock_quantity": 60, "category_id": "cat_3", "is_published": True,
                "image_urls": ["https://res.cloudinary.com/dgkpawvia/image/upload/v1781859599/ecommerce/products/green-cucumber.jpg"],
            },
            {
                "_id": "prod_9",
                "title": "Banana - Robusta (6 pcs)",
                "description": "Sweet, ripe Robusta bananas — a natural energy booster.",
                "price": 35.0, "stock_quantity": 70, "category_id": "cat_3", "is_published": True,
                "image_urls": ["https://res.cloudinary.com/dgkpawvia/image/upload/v1781859600/ecommerce/products/fresh-banana.jpg"],
            },
            {
                "_id": "prod_10",
                "title": "Tender Coconut (1 pc)",
                "description": "Fresh tender coconut full of natural, hydrating water.",
                "price": 55.0, "stock_quantity": 30, "category_id": "cat_3", "is_published": True,
                "image_urls": ["https://res.cloudinary.com/dgkpawvia/image/upload/v1781859601/ecommerce/products/tender-coconut.jpg"],
            },
        ]
        self._collections["users"] = InMemoryCollection()
        self._collections["users"]._docs = users

        self._collections["categories"] = InMemoryCollection()
        self._collections["categories"]._docs = categories
        self._collections["products"] = InMemoryCollection()
        self._collections["products"]._docs = products
        self._collections["settings"] = InMemoryCollection()
        self._collections["settings"]._docs = [{"_id": "shop_location", "lat": 28.6139, "lng": 77.2090}]

    def __getitem__(self, name):
        if name not in self._collections:
            self._collections[name] = InMemoryCollection()
        return self._collections[name]

async def connect_to_mongo():
    global client, db, _use_fallback
    try:
        import dns.resolver
        custom_resolver = dns.resolver.Resolver(configure=False)
        custom_resolver.nameservers = ['8.8.8.8', '8.8.4.4']
        dns.resolver.default_resolver = custom_resolver

        client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=3000)
        # Test the connection
        await client.admin.command('ping')
        db = client[settings.DATABASE_NAME]
        print("Connected to MongoDB")
    except Exception as e:
        print(f"MongoDB not available ({e}), using in-memory database for development")
        _use_fallback = True
        db = InMemoryDB()

async def close_mongo_connection():
    global client
    if client and not _use_fallback:
        client.close()
        print("Closed MongoDB connection")

def get_database():
    return db
