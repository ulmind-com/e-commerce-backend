from duckduckgo_search import DDGS
import json

def get_images(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.images(query, max_results=2))
            return [r['image'] for r in results]
    except Exception as e:
        print(f"Error for {query}: {e}")
        return []

print(json.dumps(get_images("Mr. Merchant Paan Shots")))
print(json.dumps(get_images("Tiny Mint Saunf")))
