import requests

url = "http://127.0.0.1:8000/api/v1/product/category/2/set_translation/"
headers = {'tenant_id': '1'}
data = {
    "lang": "en",
    "title": "Test title",
    "description": "Test description"
}

r = requests.post(url, headers=headers)