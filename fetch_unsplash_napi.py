import requests
import re
import random

def get_unsplash_ids(query):
    url = f"https://unsplash.com/napi/search/photos?query={query}&per_page=20"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/114.0.0.0"
    }
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        data = res.json()
        results = data.get("results", [])
        return [item["id"] for item in results]
    return []

queries = {
    "Kombucha Hibiscus": "kombucha red",
    "Kombucha Blueberry": "blueberry drink",
    "Aloe Vera Juice": "aloe vera drink",
    "Kombucha Original": "kombucha bottle",
    "Aam Papad": "indian candy",
    "Swad Candy": "wrapped candy",
    "Ginger Candy": "ginger candy",
    "Honey Ginger": "honey jar"
}

results = {}
for name, q in queries.items():
    ids = get_unsplash_ids(q)
    if ids:
        # Just grab the first one
        results[name] = ids[0]
    else:
        results[name] = None
        
print(results)
