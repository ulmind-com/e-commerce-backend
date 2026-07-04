from fastapi import APIRouter, HTTPException, Query
import httpx
import json

router = APIRouter()

OPENROUTER_KEY = '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'

@router.get("/reverse-geocode")
async def reverse_geocode(lat: float, lng: float):
    # Step 1: Get raw address from Nominatim
    async with httpx.AsyncClient() as client:
        try:
            nom_res = await client.get(
                f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lng}&zoom=18&addressdetails=1",
                headers={"Accept-Language": "en", "User-Agent": "OneBasket-Ecommerce/1.0"}
            )
            nom_res.raise_for_status()
            nom_data = nom_res.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to fetch location from maps provider")

    addr = nom_data.get("address", {})
    area = addr.get("neighbourhood") or addr.get("suburb") or addr.get("quarter") or addr.get("village") or ""
    city = addr.get("city") or addr.get("town") or addr.get("county") or ""
    postcode = addr.get("postcode") or ""
    
    raw = f"{area + ', ' if area else ''}{city}".strip()
    if not raw:
        raw = nom_data.get("display_name", "").split(',')[0] or "Selected Location"
        
    raw = raw.replace(" Tehsil", "").replace(" Taluka", "").replace(" Mandal", "")

    # Construct a cleaner display address by omitting unwanted administrative levels like Tehsil
    raw_display = nom_data.get("display_name", "Selected Location")
    display_parts = [p.strip() for p in raw_display.split(",")]
    clean_parts = []
    for p in display_parts:
        if "Tehsil" not in p and "Taluka" not in p and "Mandal" not in p and p not in clean_parts:
            clean_parts.append(p)
            
    display = ", ".join(clean_parts)

    # Step 2: Use AI to clean up the display address (Optional but preferred for better UI)
    try:
        async with httpx.AsyncClient() as client:
            ai_res = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost",
                    "X-Title": "OneBasket",
                },
                json={
                    "model": "meta-llama/llama-3.2-3b-instruct:free",
                    "messages": [
                        {
                            "role": "user",
                            "content": f"Given this raw address fragment: \"{raw}\", return ONLY a clean, short delivery-friendly location label (max 4 words, like \"Koramangala, Bengaluru\" or \"Andheri West, Mumbai\"). Never include words like 'Tehsil', 'Taluka' or 'Mandal'. No punctuation issues, no extra text.",
                        }
                    ],
                    "max_tokens": 30,
                    "temperature": 0.1,
                },
                timeout=3.0
            )
            if ai_res.status_code == 200:
                ai_data = ai_res.json()
                cleaned = ai_data.get("choices", [{}])[0].get("message", {}).get("content", "").strip().replace('"', '').replace("'", "")
                if cleaned and len(cleaned) < 60:
                    raw = cleaned
    except Exception:
        pass # Ignore AI failure and use raw

    return {
        "area": raw,
        "display": display
    }

@router.get("/search")
async def search_location(q: str = Query(..., min_length=2)):
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(
                f"https://nominatim.openstreetmap.org/search?format=json&q={q}&limit=5",
                headers={"Accept-Language": "en", "User-Agent": "OneBasket-Ecommerce/1.0"}
            )
            res.raise_for_status()
            return res.json()
        except Exception:
            raise HTTPException(status_code=500, detail="Search failed")
