"""Seed sample products and categories for development."""
import urllib.request
import json
import time

API_BASE = "http://localhost:8000/api"

# Login as admin to get token
from urllib.parse import urlencode
login_data = urlencode({"username": "admin@aura.com", "password": "admin123"}).encode()
try:
    req = urllib.request.Request(f"{API_BASE}/auth/login", data=login_data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    resp = urllib.request.urlopen(req)
    login_result = json.loads(resp.read().decode())
    token = login_result["access_token"]
    print(f"Login successful, got token")
except Exception as e:
    print(f"Login failed: {e}")
    exit(1)

auth_headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}

# Clear database before seeding
try:
    req = urllib.request.Request(f"{API_BASE}/admin/clear-db", headers=auth_headers, method="POST")
    resp = urllib.request.urlopen(req)
    print("Database cleared successfully.")
except Exception as e:
    print(f"Failed to clear database: {e}")

# Create categories
categories = [
    {"name": "Fresh Fruits", "description": "Fresh and healthy fruits", "slug": "fresh-fruits", "is_active": True},
    {"name": "Pharmacy", "description": "Medicines and health care", "slug": "pharmacy", "is_active": True},
    {"name": "Pet Care", "description": "Pet food and supplies", "slug": "pet-care", "is_active": True},
    {"name": "Baby Care", "description": "Baby products and diapers", "slug": "baby-care", "is_active": True},
    {"name": "Dairy, Bread & Eggs", "description": "Fresh milk, bread, and farm eggs", "slug": "dairy-bread-eggs", "is_active": True},
]

cat_ids = []
for cat in categories:
    try:
        req = urllib.request.Request(f"{API_BASE}/categories/", data=json.dumps(cat).encode(), headers=auth_headers)
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read().decode())
        cat_ids.append(result.get("_id", result.get("id")))
        print(f"Category created: {cat['name']}")
    except Exception as e:
        print(f"Category '{cat['name']}' error: {e}")
        cat_ids.append("unknown")

# We will use realistic Unsplash URLs that are extremely common and unlikely to 404.
products = [
    # Fresh Fruits
    {"title": "Fresh Kashmiri Apple", "description": "4 pcs.", "price": 149.00, "stock_quantity": 50, "category_id": cat_ids[0], "image_urls": ["https://images.unsplash.com/photo-1560806887-1e4cd0b6faa6?w=400&h=400&fit=crop"], "is_published": True},
    {"title": "Robusta Banana", "description": "1 kg pack.", "price": 69.00, "stock_quantity": 40, "category_id": cat_ids[0], "image_urls": ["https://images.unsplash.com/photo-1571501478200-b5b4a6bc9f58?w=400&h=400&fit=crop"], "is_published": True},
    {"title": "Fresh Orange", "description": "1 kg bag.", "price": 120.00, "stock_quantity": 30, "category_id": cat_ids[0], "image_urls": ["https://images.unsplash.com/photo-1611080626919-7cf5a9dbab5b?w=400&h=400&fit=crop"], "is_published": True},
    {"title": "Green Grapes", "description": "500 g.", "price": 99.00, "stock_quantity": 60, "category_id": cat_ids[0], "image_urls": ["https://images.unsplash.com/photo-1537640538966-79f369143f8f?w=400&h=400&fit=crop"], "is_published": True},
    {"title": "Watermelon", "description": "1 pc (approx 2.5 kg).", "price": 150.00, "stock_quantity": 25, "category_id": cat_ids[0], "image_urls": ["https://images.unsplash.com/photo-1589984662646-e7b2e4962f18?w=400&h=400&fit=crop"], "is_published": True},

    # Pharmacy
    {"title": "Honitus Cough Syrup", "description": "100 ml.", "price": 110.00, "stock_quantity": 100, "category_id": cat_ids[1], "image_urls": ["https://images.unsplash.com/photo-1584017911766-d451b3d0e843?w=400&h=400&fit=crop"], "is_published": True},
    {"title": "Volini Pain Relief Spray", "description": "60 g.", "price": 199.00, "stock_quantity": 80, "category_id": cat_ids[1], "image_urls": ["https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=400&h=400&fit=crop"], "is_published": True},
    {"title": "Crocin Advance", "description": "15 tablets.", "price": 20.00, "stock_quantity": 200, "category_id": cat_ids[1], "image_urls": ["https://images.unsplash.com/photo-1631549916768-4119b2e5f926?w=400&h=400&fit=crop"], "is_published": True},
    {"title": "Vicks VapoRub", "description": "50 g.", "price": 150.00, "stock_quantity": 120, "category_id": cat_ids[1], "image_urls": ["https://images.unsplash.com/photo-1584362917165-526a968579e8?w=400&h=400&fit=crop"], "is_published": True},

    # Pet Care
    {"title": "Pedigree Adult Dog Food", "description": "3 kg bag.", "price": 650.00, "stock_quantity": 50, "category_id": cat_ids[2], "image_urls": ["https://images.unsplash.com/photo-1589924691995-400dc9ecc119?w=400&h=400&fit=crop"], "is_published": True},
    {"title": "Whiskas Cat Food", "description": "1.2 kg bag.", "price": 350.00, "stock_quantity": 30, "category_id": cat_ids[2], "image_urls": ["https://images.unsplash.com/photo-1623387641168-d9803ddd3f35?w=400&h=400&fit=crop"], "is_published": True},
    {"title": "Dog Chew Bone", "description": "2 pcs.", "price": 149.00, "stock_quantity": 40, "category_id": cat_ids[2], "image_urls": ["https://images.unsplash.com/photo-1535930891776-0c2dfb7fda1a?w=400&h=400&fit=crop"], "is_published": True},
    {"title": "Cat Litter Sand", "description": "5 kg.", "price": 450.00, "stock_quantity": 20, "category_id": cat_ids[2], "image_urls": ["https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=400&h=400&fit=crop"], "is_published": True},

    # Baby Care
    {"title": "Pampers Active Baby Diapers", "description": "Large size, 50 count.", "price": 799.00, "stock_quantity": 80, "category_id": cat_ids[3], "image_urls": ["https://images.unsplash.com/photo-1519689680058-324335c77eba?w=400&h=400&fit=crop"], "is_published": True},
    {"title": "Johnson's Baby Lotion", "description": "500 ml.", "price": 320.00, "stock_quantity": 60, "category_id": cat_ids[3], "image_urls": ["https://images.unsplash.com/photo-1555252333-9f8e92e65df9?w=400&h=400&fit=crop"], "is_published": True},
    {"title": "Baby Wipes", "description": "Pack of 72 wipes.", "price": 150.00, "stock_quantity": 100, "category_id": cat_ids[3], "image_urls": ["https://images.unsplash.com/photo-1512438248247-f0f2a5a8b7f0?w=400&h=400&fit=crop"], "is_published": True},
    {"title": "Himalaya Baby Powder", "description": "400 g.", "price": 250.00, "stock_quantity": 50, "category_id": cat_ids[3], "image_urls": ["https://images.unsplash.com/photo-1522771930-78848d9293e8?w=400&h=400&fit=crop"], "is_published": True},

    # Dairy, Bread & Eggs
    {"title": "Amul Taaza Toned Fresh Milk", "description": "500 ml pouch.", "price": 27.00, "stock_quantity": 150, "category_id": cat_ids[4], "image_urls": ["https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&h=400&fit=crop"], "is_published": True},
    {"title": "Farm Fresh White Eggs", "description": "Pack of 6.", "price": 65.00, "stock_quantity": 100, "category_id": cat_ids[4], "image_urls": ["https://images.unsplash.com/photo-1587486913049-53fc88980bfc?w=400&h=400&fit=crop"], "is_published": True},
    {"title": "Harvest Gold White Bread", "description": "400 g pack.", "price": 40.00, "stock_quantity": 60, "category_id": cat_ids[4], "image_urls": ["https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400&h=400&fit=crop"], "is_published": True},
    {"title": "Mother Dairy Classic Dahi", "description": "400 g cup.", "price": 35.00, "stock_quantity": 80, "category_id": cat_ids[4], "image_urls": ["https://images.unsplash.com/photo-1628088062854-d1870b4553da?w=400&h=400&fit=crop"], "is_published": True},
]

for prod in products:
    try:
        req = urllib.request.Request(f"{API_BASE}/products", data=json.dumps(prod).encode(), headers=auth_headers)
        resp = urllib.request.urlopen(req)
        print(f"Product created: {prod['title']}")
    except Exception as e:
        print(f"Product '{prod['title']}' error: {e}")

print("\nSeeding complete! Visit http://localhost:5173 to see the products.")
