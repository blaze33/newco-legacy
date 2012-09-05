from affiliation.amazon.utils import amazon_item_search
from affiliation.decathlon.tools import decathlon_item_search


def stores_item_search(keyword, nb_items=5):
    item_list_by_store = dict()
    if keyword != "":
        item_list_by_store.update({
            "amazon": amazon_item_search(keyword, nb_items=nb_items),
            "decathlon": decathlon_item_search(keyword, nb_items=nb_items),
        })
    return item_list_by_store
