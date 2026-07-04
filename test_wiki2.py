import requests
import urllib.parse
import json

HEADERS = {
    "User-Agent": "EcommercePlatformScript/1.0 (admin@ecommerce.com) Python/3.10"
}

def search_wikimedia_commons(query):
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(query)}&gsrnamespace=6&gsrlimit=2&prop=imageinfo&iiprop=url&format=json"
    try:
        res = requests.get(url, headers=HEADERS)
        data = res.json()
        pages = data.get("query", {}).get("pages", {})
        urls = []
        for page_id, page_info in pages.items():
            imageinfo = page_info.get("imageinfo", [])
            if imageinfo:
                urls.append(imageinfo[0].get("url"))
        return urls
    except Exception as e:
        pass
    return []

queries = [
    "Red Apple Fruit",
    "Banana Fruit",
    "Floor cleaner bottle"
]

results = {}
for q in queries:
    results[q] = search_wikimedia_commons(q)
    
print(json.dumps(results, indent=2))
