from django.core.exceptions import ObjectDoesNotExist
from django.db import models

# Static data. Probably shouldn't be in the DB
STORES = {
    "Amazon": {"name": "Amazon", "url": "http://www.amazon.fr"},
    "Decathlon": {"name": "Decathlon", "url": "http://www.decathlon.fr"},
}


class StoreManager(models.Manager):
    def get_store(self, store_name):
        if store_name not in STORES:
            return None
        try:
            store = self.get(name=store_name)
        except ObjectDoesNotExist:
            store_entry = STORES.get(store_name)
            store, created = self.get_or_create(**store_entry)
        return store
