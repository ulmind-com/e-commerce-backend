import requests

def test_unsplash(photo_id):
    url = f"https://images.unsplash.com/photo-{photo_id}?w=600"
    res = requests.head(url)
    print(f"{photo_id}: {res.status_code}")

ids = [
    "1560806887-1e4cd0b6faa6", # Apple
    "1571501478200-b5b4a6bc9f58", # Banana
    "1584820927508-0118357eb482" # Lizol
]

for i in set(ids):
    test_unsplash(i)
