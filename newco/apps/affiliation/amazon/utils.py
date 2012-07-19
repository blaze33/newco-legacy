import os

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_ASSOCIATE_TAG = os.environ.get('AWS_ASSOCIATE_TAG')
AWS_LOCALE = os.environ.get('AWS_LOCALE')

from amazonproduct import API
from affiliation.models import AffiliationItem


def amazon_item_search(keyword, search_index="All"):

    api = API(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_LOCALE)
    node = api.item_search(search_index, Keywords=keyword,
                        ResponseGroup="Large", AssociateTag=AWS_ASSOCIATE_TAG)

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
        for item in items:
            item_list.append(AmazonSearchItem(
                                asin=item.ASIN,
                                title=item.ItemAttributes.Title.pyval,
                                locale=AWS_LOCALE
            ))
            print 'ASIN: %s, Title: %s' % (item.ASIN,
                                            item.ItemAttributes.Title.pyval)

        if current_page == 10:
            break

    return item_list


class AmazonSearchItem(object):

    def __init__(self, asin, title, locale):
        self.asin = asin
        self.title = title
        self.locale = locale

    def __unicode__(self):
        return "ASIN: %s, Title: %s" % (self.asin, self.title[:10])

    def __str__(self):
        return self.__unicode__()

    def register(self):
        api = API(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, self.locale)
        root = api.item_lookup(self.asin, ResponseGroup='Large',
                                AssociateTag=AWS_ASSOCIATE_TAG).Items.Item
