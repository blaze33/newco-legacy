from urllib2 import URLError
from math import ceil

from django.conf import settings

from amazonproduct import API
from amazonproduct.errors import NoExactMatchesFound


def amazon_product_search(keyword, storing_class, store,
                          search_index="All", nb_items=10):
    api = API(settings.AWS_PRODUCT_ACCESS_KEY_ID,
              settings.AWS_PRODUCT_SECRET_ACCESS_KEY, settings.AWS_LOCALE)

    try:
        node = api.item_search(search_index, Keywords=keyword,
                               ResponseGroup="Large",
                               AssociateTag=settings.AWS_ASSOCIATE_TAG)
    except NoExactMatchesFound:
        return None
    except URLError:
        if settings.DEBUG:
            raise
        else:
            return None

    nb_pages = int(ceil(nb_items * 0.1))

    item_list = []

    for root in node:
#        total_results = root.Items.TotalResults.pyval
#        total_pages = root.Items.TotalPages.pyval
        try:
            current_page = root.Items.Request.ItemSearchRequest.ItemPage.pyval
        except AttributeError:
            current_page = 1

        nspace = root.nsmap.get(None, '')
        items = root.xpath('//aws:Items/aws:Item', namespaces={'aws': nspace})

        item_list.extend(items)

        if current_page >= nb_pages:
            break

    counter = 0
    aff_item_list = list()
    for item in item_list:
        entry, created = storing_class.objects.get_or_create(
            store=store, object_id=item.ASIN)
        entry.store_init(store, item)
        entry.save()
        if entry.item is None:
            aff_item_list.append(entry)
            counter += 1
            if counter == nb_items:
                break

    return aff_item_list
