from affiliation.amazon.tools import amazon_product_search
from affiliation.decathlon.tools import decathlon_product_search
from affiliation.models import AffiliationItem, Store


def stores_product_search(keyword, nb_items=5):
    product_list_by_store = {}
    if keyword != "":
        amazon = Store.objects.get_store("Amazon")
        decathlon = Store.objects.get_store("Decathlon")
        product_list_by_store.update({
            "amazon": amazon_product_search(
                keyword, AffiliationItem, amazon, nb_items=nb_items),
            "decathlon": decathlon_product_search(
                keyword, AffiliationItem, decathlon, nb_items=nb_items),
        })
    return product_list_by_store
