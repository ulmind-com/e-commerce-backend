import cloudinary, cloudinary.uploader

cloudinary.config(
    cloud_name="dgkpawvia",
    api_key="567717278787649",
    api_secret="t9q4ZjJqBmsFjpYLJfJWkwEpDG8",
    secure=True,
)

# Cloudinary can fetch URLs directly — bypasses CDN 403s
remaining = [
    ("britannia-white-bread", "https://cdn.grofers.com/app/images/products/full_screen/462989_A.jpg"),
    ("farm-fresh-eggs",       "https://cdn.grofers.com/app/images/products/full_screen/305040_A.jpg"),
    ("lays-chips",            "https://cdn.grofers.com/app/images/products/full_screen/246835_A.jpg"),
    ("green-cucumber",        "https://cdn.grofers.com/app/images/products/full_screen/439162_A.jpg"),
    ("fresh-banana",          "https://cdn.grofers.com/app/images/products/full_screen/366447_A.jpg"),
    ("tender-coconut",        "https://cdn.grofers.com/app/images/products/full_screen/391063_A.jpg"),
]

for slug, url in remaining:
    try:
        result = cloudinary.uploader.upload(
            url,
            public_id=slug,
            folder="ecommerce/products",
            overwrite=True,
            resource_type="image",
            quality="auto",
            fetch_format="auto",
        )
        secure = result.get("secure_url", "no url")
        print(f"[OK] {slug}: {secure}")
    except Exception as e:
        print(f"[FAIL] {slug}: {e}")
