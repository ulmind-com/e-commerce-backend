"""
Script: upload_product_images_to_cloudinary.py

Downloads product images from Blinkit's CDN and re-uploads them
to our own Cloudinary account (dgkpawvia), then prints the final
Cloudinary URLs to use in seed_catalog.py.
"""

import cloudinary
import cloudinary.uploader
import urllib.request
import json
import time

# ── Cloudinary config ─────────────────────────────────────────────────────────
cloudinary.config(
    cloud_name="dgkpawvia",
    api_key="567717278787649",
    api_secret="t9q4ZjJqBmsFjpYLJfJWkwEpDG8",
    secure=True,
)

# ── Products sourced from Blinkit ─────────────────────────────────────────────
# 6 original products + 4 new ones (eggs, bread, banana, cucumber expanded)
products = [
    {
        "slug": "amul-buffalo-a2-milk",
        "title": "Amul Buffalo A2 Milk (1 ltr)",
        "description": "Rich, creamy, and nutritious A2 buffalo milk from Amul. Great for everyday use.",
        "price": 90.0,
        "category": "Dairy, Bread & Eggs",
        "source_url": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=900/da/cms-assets/cms/product/a53bb288-2ff6-478a-aadc-5e982262fa3e.jpg",
    },
    {
        "slug": "amul-masti-curd",
        "title": "Amul Masti Pouch Curd (400 g)",
        "description": "Thick and tasty curd, perfect for meals, raita, and lassi.",
        "price": 35.0,
        "category": "Dairy, Bread & Eggs",
        "source_url": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=900/da/cms-assets/cms/product/d7a0818e-c466-4ffb-ac15-8156ccc27d90.jpg",
    },
    {
        "slug": "britannia-white-bread",
        "title": "Britannia Soft White Bread (400 g)",
        "description": "Soft, fresh white sandwich bread perfect for every morning.",
        "price": 40.0,
        "category": "Dairy, Bread & Eggs",
        "source_url": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=900/app/images/products/full_screen/462989_A.jpg",
    },
    {
        "slug": "farm-fresh-eggs",
        "title": "Farm Fresh Eggs (6 pcs)",
        "description": "Fresh, protein-packed farm eggs — essential for every kitchen.",
        "price": 65.0,
        "category": "Dairy, Bread & Eggs",
        "source_url": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=900/app/images/products/full_screen/305040_A.jpg",
    },
    {
        "slug": "real-fruit-juice",
        "title": "Real Fruit Power Mixed Fruit Juice (1 ltr)",
        "description": "Refreshing mixed fruit juice made with real fruit. No added preservatives.",
        "price": 103.0,
        "category": "Snacks & Drinks",
        "source_url": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=900/da/cms-assets/cms/product/ff4a3ece-1ddf-4860-b293-c2c22c768bb6.jpg",
    },
    {
        "slug": "hide-seek-cookies",
        "title": "Hide & Seek Chocolate Chip Cookies (200 g)",
        "description": "Crunchy choco-chip cookies for your sweet cravings. Great with milk or tea.",
        "price": 48.0,
        "category": "Snacks & Drinks",
        "source_url": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=900/da/cms-assets/cms/product/rc-upload-1776829632782-4.jpg",
    },
    {
        "slug": "lays-chips-classic",
        "title": "Lay's Classic Salted Chips (73 g)",
        "description": "Light, crispy, and perfectly salted potato chips — the original snack.",
        "price": 30.0,
        "category": "Snacks & Drinks",
        "source_url": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=900/app/images/products/full_screen/246835_A.jpg",
    },
    {
        "slug": "green-cucumber",
        "title": "Green Cucumber (500 g)",
        "description": "Fresh, crunchy cucumbers. Perfect for salads, raita, and healthy snacking.",
        "price": 25.0,
        "category": "Vegetables & Fruits",
        "source_url": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=900/app/images/products/full_screen/439162_A.jpg",
    },
    {
        "slug": "fresh-banana",
        "title": "Banana - Robusta (6 pcs)",
        "description": "Sweet, ripe Robusta bananas — a natural energy booster anytime.",
        "price": 35.0,
        "category": "Vegetables & Fruits",
        "source_url": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=900/app/images/products/full_screen/366447_A.jpg",
    },
    {
        "slug": "tender-coconut",
        "title": "Tender Coconut (1 pc)",
        "description": "Fresh tender coconut full of natural, hydrating water.",
        "price": 55.0,
        "category": "Vegetables & Fruits",
        "source_url": "https://cdn.grofers.com/cdn-cgi/image/f=auto,fit=scale-down,q=70,metadata=none,w=900/app/images/products/full_screen/391063_A.jpg",
    },
]


def download_bytes(url: str) -> bytes | None:
    """Download a URL and return raw bytes."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read()
    except Exception as e:
        print(f"  [DOWNLOAD ERROR] {e}")
        return None


def upload_to_cloudinary(image_bytes: bytes, public_id: str) -> str | None:
    """Upload bytes to Cloudinary and return secure URL."""
    try:
        result = cloudinary.uploader.upload(
            image_bytes,
            public_id=public_id,
            folder="ecommerce/products",
            overwrite=True,
            resource_type="image",
            quality="auto",
            fetch_format="auto",
        )
        return result.get("secure_url")
    except Exception as e:
        print(f"  [CLOUDINARY ERROR] {e}")
        return None


def main():
    results = []
    print(f"\n{'='*60}")
    print("  Uploading product images to Cloudinary (dgkpawvia)")
    print(f"{'='*60}\n")

    for i, product in enumerate(products, 1):
        print(f"[{i}/{len(products)}] {product['title']}")
        print(f"  Downloading from: {product['source_url'][:70]}...")

        image_bytes = download_bytes(product["source_url"])
        if not image_bytes:
            print("  [FAIL] Download failed, skipping.")
            results.append({**product, "cloudinary_url": None})
            continue

        print(f"  Downloaded {len(image_bytes):,} bytes")
        print(f"  Uploading to Cloudinary as: ecommerce/products/{product['slug']}")

        cloudinary_url = upload_to_cloudinary(image_bytes, product["slug"])
        if cloudinary_url:
            print(f"  [OK] Cloudinary URL: {cloudinary_url}")
        else:
            print("  [FAIL] Upload failed")

        results.append({**product, "cloudinary_url": cloudinary_url})
        time.sleep(0.5)  # Avoid rate limiting

    print(f"\n{'='*60}")
    print("  RESULTS SUMMARY")
    print(f"{'='*60}\n")
    success = [r for r in results if r["cloudinary_url"]]
    print(f"  Successful: {len(success)}/{len(results)}\n")

    # Print the Python dict for use in seed_catalog.py
    print("\n# ── Paste this into seed_catalog.py → products list ──────────────\n")
    for r in results:
        url = r["cloudinary_url"] or r["source_url"]
        print(f'    # {r["title"]}')
        print(f'    "image_urls": ["{url}"],')
        print()

    # Also dump full JSON for reference
    with open("cloudinary_upload_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nFull results saved to: cloudinary_upload_results.json")

    return results


if __name__ == "__main__":
    main()
