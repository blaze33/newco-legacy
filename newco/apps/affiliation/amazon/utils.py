from django.conf import settings
from amazonproduct import API


def amazon_item_search(keyword, search_index="All"):

    api = API(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY,
                                                        settings.AWS_LOCALE)
    node = api.item_search(search_index, Keywords=keyword,
                                    ResponseGroup="Large",
                                    AssociateTag=settings.AWS_ASSOCIATE_TAG)

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

        if current_page == 1:
            break

    return item_list
