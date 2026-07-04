import urllib.request

def test_flickr():
    url = 'https://loremflickr.com/400/400/dahi'
    try:
        req = urllib.request.Request(url, method='HEAD')
        resp = urllib.request.urlopen(req)
        print("Final URL:", resp.url)
    except Exception as e:
        print('Error:', e)

test_flickr()
