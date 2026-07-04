import urllib.request
import json
from urllib.parse import urlencode

API = "http://localhost:8000/api"

# Login
login_data = urlencode({"username": "admin@aura.com", "password": "admin123"}).encode()
req = urllib.request.Request(f"{API}/auth/login", data=login_data, headers={"Content-Type": "application/x-www-form-urlencoded"})
resp = urllib.request.urlopen(req)
token = json.loads(resp.read().decode())["access_token"]
headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

# Image mapping
IMAGE_UPDATES = {
    "Mr. Merchant Paan Shots": ["https://images.unsplash.com/photo-1628556270448-4d4e4148e1b1?w=400&q=80"],  # Mint
    "Sugar Coated Saunf": ["https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=400&q=80"],  # Spices
    "Nature's Trunk Ginger Digestive Candy": ["https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=400&q=80"],  # Spices
    "Hexhive Honey Ginger Digestives": ["https://images.unsplash.com/photo-1587049352851-8d4e89133924?w=400&q=80"],  # Honey
    "Farm Fresh White Eggs": ["https://images.unsplash.com/photo-1506976785307-8732e854ad03?w=400&q=80"],  # Eggs
    "Fresh Kashmiri Apple": ["https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?w=400&q=80"],  # Apple
    "Robusta Banana": ["https://images.unsplash.com/photo-1528825871115-3581a5387919?w=400&q=80"],  # Banana
}

# Get all products
r2 = urllib.request.urlopen(f"{API}/products?limit=200")
prods = json.loads(r2.read().decode())

updated_count = 0
for p in prods:
    title = p.get("title")
    if title in IMAGE_UPDATES:
        pid = p.get("_id") or p.get("id")
        
        # Prepare the full payload because PUT expects all required fields
        payload = {
            "title": p.get("title"),
            "description": p.get("description", ""),
            "price": p.get("price"),
            "stock_quantity": p.get("stock_quantity"),
            "category_id": p.get("category_id"),
            "image_urls": IMAGE_UPDATES[title],
            "is_published": p.get("is_published", True)
        }
        
        data = json.dumps(payload).encode()
        update_req = urllib.request.Request(f"{API}/products/{pid}", data=data, headers=headers, method="PUT")
        try:
            urllib.request.urlopen(update_req)
            print(f"Updated images for: {title}")
            updated_count += 1
        except Exception as e:
            print(f"Failed to update {title}: {e}")

print(f"\nDone! Updated {updated_count} products.")
