import requests

from django.conf import settings


def search_images(query):
    payload = {
        'q': query,
        'cx': settings.GOOGLE_SEARCH_ENGINE_ID,
        'key': settings.GOOGLE_API_KEY,
        'searchType': 'image',
    }
    r = requests.get("https://www.googleapis.com/customsearch/v1",
                     params=payload)
    if not r.ok:
        if r.status_code == 403:
            # send msg to logger
            pass
    return flatten(r)


def flatten(r):
    flat = []
    for i in r.json.get("items", []):
        i.update(i.pop('image'))
        flat.append(i)
    return flat
