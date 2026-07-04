from playwright.sync_api import sync_playwright
import urllib.parse
import json

def test_ddg(query):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # Navigate to DDG images
        url = f"https://duckduckgo.com/?q={urllib.parse.quote(query)}&iax=images&ia=images"
        page.goto(url, wait_until="networkidle")
        
        # Extract images
        imgs = page.evaluate('''() => {
            const images = Array.from(document.querySelectorAll('img.tile--img__img'));
            return images.map(img => img.src).filter(src => src && src.startsWith('http'));
        }''')
        browser.close()
        return imgs[:2]

print(json.dumps(test_ddg("Mr. Merchant Paan Shots product packaging"), indent=2))
