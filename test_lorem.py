import requests

def test_url(url):
    r = requests.head(url, allow_redirects=True)
    print(f"{url} -> {r.status_code}")

test_url("https://loremflickr.com/600/600/spice")
test_url("https://loremflickr.com/600/600/candy")
test_url("https://loremflickr.com/600/600/kombucha")
test_url("https://loremflickr.com/600/600/ghee")
