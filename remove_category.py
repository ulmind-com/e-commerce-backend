"""Remove duplicate 'Dairy, Bread & Eggs' category and its products."""
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

# Find duplicate categories
r = urllib.request.urlopen(f"{API}/categories/")
cats = json.loads(r.read().decode())
dairy_cats = [c for c in cats if c["name"] == "Dairy, Bread & Eggs"]
print(f"Found {len(dairy_cats)} 'Dairy, Bread & Eggs' categories")

if len(dairy_cats) < 2:
    print("No duplicate found, nothing to do.")
    exit()

KEEP_ID = dairy_cats[0].get("_id") or dairy_cats[0].get("id")
DELETE_ID = dairy_cats[1].get("_id") or dairy_cats[1].get("id")
print(f"Keeping: {KEEP_ID}")
print(f"Deleting: {DELETE_ID}")

# Get all products
r2 = urllib.request.urlopen(f"{API}/products")
prods = json.loads(r2.read().decode())

keep_titles = set(p["title"] for p in prods if p.get("category_id") == KEEP_ID)
dupes = [p for p in prods if p.get("category_id") == DELETE_ID]

for p in dupes:
    pid = p.get("_id") or p.get("id")
    title = p.get("title", "Unknown")
    if title in keep_titles:
        # Duplicate product — delete it
        req = urllib.request.Request(f"{API}/products/{pid}", headers=headers, method="DELETE")
        urllib.request.urlopen(req)
        print(f"  Deleted duplicate product: {title}")
    else:
        # Unique product — move to kept category
        data = json.dumps({"category_id": KEEP_ID}).encode()
        req = urllib.request.Request(f"{API}/products/{pid}", data=data, headers=headers, method="PUT")
        urllib.request.urlopen(req)
        print(f"  Moved product to kept category: {title}")

# Delete the duplicate category
req = urllib.request.Request(f"{API}/categories/{DELETE_ID}", headers=headers, method="DELETE")
urllib.request.urlopen(req)
print(f"\nDeleted duplicate category: {DELETE_ID}")
print("Done!")
