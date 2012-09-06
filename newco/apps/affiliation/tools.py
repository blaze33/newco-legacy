from affiliation.amazon.tools import amazon_product_search
from affiliation.decathlon.tools import decathlon_product_search


def stores_product_search(keyword, nb_items=5):
    product_list_by_store = dict()
    if keyword != "":
        product_list_by_store.update({
            "amazon": amazon_product_search(keyword, nb_items=nb_items),
            "decathlon": decathlon_product_search(keyword, nb_items=nb_items),
        })
    return product_list_by_store
