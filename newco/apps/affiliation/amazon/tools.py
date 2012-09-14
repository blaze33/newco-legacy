from urllib2 import URLError
from math import ceil

from django.conf import settings

from amazonproduct import API
from amazonproduct.errors import NoExactMatchesFound

from affiliation.models import AffiliationItem, AffiliationItemCatalog, Store


def amazon_product_search(keyword, search_index="All", nb_items=10):
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
    except URLError, e:
        print e.message
        if settings.DEBUG:
            raise URLError("Problem with amazon connexion.\n%s" % e.message)
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
        entry, created = AffiliationItemCatalog.objects.get_or_create(
            store=amazon, object_id=item.ASIN
        )
        entry.store_init("amazon", item)
        entry.save()
        if AffiliationItem.objects.filter(object_id=entry.object_id,
                                            store=amazon).count() == 0:
            aff_item_list.append(entry)
            counter += 1
            if counter == nb_items:
                break

    return aff_item_list
