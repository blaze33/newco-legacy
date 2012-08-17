from django.conf import settings
from amazonproduct import API
from amazonproduct.errors import NoExactMatchesFound
from affiliation.models import AffiliationItemCatalog, Store
from math import ceil


def amazon_item_search(keyword, search_index="All", nb_items=10):
    amazon, created = Store.objects.get_or_create(
        name="Amazon", url="http://www.amazon.fr"
    )

    api = API(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY,
                                                        settings.AWS_LOCALE)

    try:
        node = api.item_search(search_index, Keywords=keyword,
                                    ResponseGroup="Large",
                                    AssociateTag=settings.AWS_ASSOCIATE_TAG)
    except NoExactMatchesFound:
        return None

    nb_pages = int(ceil(nb_items * 0.1))

    item_list = []

    for root in node:
        total_results = root.Items.TotalResults.pyval
        total_pages = root.Items.TotalPages.pyval
        try:
            current_page = root.Items.Request.ItemSearchRequest.ItemPage.pyval
        except AttributeError:
            current_page = 1

        print 'page %d of %d' % (current_page, total_pages)

        nspace = root.nsmap.get(None, '')
        items = root.xpath('//aws:Items/aws:Item', namespaces={'aws': nspace})

        item_list.extend(items)

        if current_page >= nb_pages:
            break

    item_list = item_list[:nb_items]
    aff_item_list = list()
    for item in item_list:
        entry, created = AffiliationItemCatalog.objects.get_or_create(
            store=amazon, object_id=item.ASIN
        )
        entry.store_init("amazon", item)
        entry.save()
        aff_item_list.append(entry)

    return aff_item_list
