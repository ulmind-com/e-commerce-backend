import cloudinary, cloudinary.uploader

cloudinary.config(
    cloud_name="dgkpawvia",
    api_key="567717278787649",
    api_secret="t9q4ZjJqBmsFjpYLJfJWkwEpDG8",
    secure=True,
)

base = r"C:\Users\Swastika Roy\.gemini\antigravity-ide\brain\4a776981-3548-4edc-867d-3ea149fbcc00"

files = [
    ("britannia-white-bread", f"{base}\\britannia_bread_1781859479167.png"),
    ("farm-fresh-eggs",       f"{base}\\farm_eggs_1781859495876.png"),
    ("lays-chips",            f"{base}\\lays_chips_1781859513965.png"),
    ("green-cucumber",        f"{base}\\green_cucumber_1781859532105.png"),
    ("fresh-banana",          f"{base}\\fresh_banana_1781859552136.png"),
    ("tender-coconut",        f"{base}\\tender_coconut_1781859567402.png"),
]

for slug, path in files:
    try:
        with open(path, "rb") as f:
            data = f.read()
        result = cloudinary.uploader.upload(
            data,
            public_id=slug,
            folder="ecommerce/products",
            overwrite=True,
            resource_type="image",
            quality="auto",
            fetch_format="auto",
        )
        print(f"[OK] {slug}: {result['secure_url']}")
    except Exception as e:
        print(f"[FAIL] {slug}: {e}")
