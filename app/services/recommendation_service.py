import os
import json
from groq import Groq
import traceback

def get_similar_products(target_product: dict, candidates: list) -> list:
    """
    Uses the Groq API to rank candidate products by similarity to the target product.
    Returns a list of up to 5 similar product IDs.
    """
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        print("GROQ_API_KEY is not set. Falling back to simple randomized/first-N selection.")
        # Fallback if no API key
        return [c["_id"] for c in candidates if c["_id"] != target_product.get("_id")][:5]

    try:
        client = Groq(api_key=groq_api_key)
        
        # Prepare target product summary
        target_info = f"ID: {target_product.get('_id')}\nTitle: {target_product.get('title')}\nDescription: {target_product.get('description')}"
        
        # Prepare candidates summary (excluding target)
        candidate_list_str = ""
        for c in candidates:
            if str(c["_id"]) == str(target_product.get("_id")):
                continue
            candidate_list_str += f"ID: {c['_id']}, Title: {c.get('title')}\n"

        if not candidate_list_str:
            return []

        prompt = f"""You are an advanced ML recommendation engine for an e-commerce platform.
Your task is to find the most similar products to a target product.

TARGET PRODUCT:
{target_info}

CANDIDATE PRODUCTS:
{candidate_list_str}

Analyze the target product's title and description. Compare it with the candidate products.
Return a JSON object containing a single key "similar_ids" which is an array of up to 5 product IDs from the candidates that are most similar/relevant to the target product.
Example output: {{"similar_ids": ["id1", "id2", "id3"]}}
"""
        
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a JSON-only API. You must strictly output valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama3-8b-8192",
            temperature=0.1,
            max_tokens=200,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        data = json.loads(content)
        return data.get("similar_ids", [])
    except Exception as e:
        print("Groq API error:", e)
        traceback.print_exc()
        return [c["_id"] for c in candidates if str(c["_id"]) != str(target_product.get("_id"))][:5]
