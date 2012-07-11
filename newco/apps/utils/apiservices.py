import requests
from django.conf import settings

def search_images(query):
    payload = {
        'q': query,
        'cx': settings.GOOGLE_SEARCH_ENGINE_ID,
        'key': settings.GOOGLE_API_KEY,
        'searchType': 'image',
        }
    r = requests.get("https://www.googleapis.com/customsearch/v1", params=payload)
    return r
