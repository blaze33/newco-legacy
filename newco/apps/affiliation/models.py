from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from decimal import Decimal

from model_utils import Choices

from items.models import Item


class Store(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("name"))
    url = models.URLField(max_length=200, verbose_name=_("url_webapp"))
    slug = models.SlugField(verbose_name=_("slug"), editable=False)
    last_modified = models.DateTimeField(auto_now=True,
                                         verbose_name=_("last modified"))
    url_catalog = models.URLField(max_length=200, verbose_name=_("url_catalog"))
    

    class Meta:
        verbose_name = _("store")

    def __unicode__(self):
        return u"%s" % (self.name)

    def save(self):
        self.slug = slugify(self.name)
        super(Store, self).save()


class AffiliationItem(models.Model):
    CURRENCIES = Choices(
        (0, "euro", _("Euro")),
        (1, "dollar", _("Dollar")),
        (2, "pound", _("Pound"))
    )

    item = models.ForeignKey(Item)
    name_at_store = models.CharField(max_length=100, verbose_name=_("name at store"))
    ref_catalog = models.IntegerField(default=0, verbose_name=_("ref_catalog"))
    store = models.ForeignKey(Store, verbose_name=_("store"))
    url = models.URLField(max_length=600, verbose_name=_("url"))
    url_img = models.URLField(max_length=200, verbose_name=_("url img"))
    url_img_s = models.URLField(max_length=200, verbose_name=_("url img small"))
    ean = models.IntegerField(default=0, verbose_name=_("EAN"))
    price = models.DecimalField(default=0, max_digits=16, decimal_places=2,
                                        verbose_name=_("price"))
    currency = models.SmallIntegerField(choices=CURRENCIES,
                                        default=CURRENCIES.euro,
                                        verbose_name=_("currency"))
    creation_date = models.DateTimeField(default=timezone.now, editable=False,
                                        verbose_name=_("date created"))
    update_date = models.DateTimeField(auto_now=True,
                                        verbose_name=_("last modified"))

    class Meta:
        verbose_name = _("affiliation item")
        unique_together = (('store', 'ref_catalog'),) #TO GAS: changed object_ref to ean because Decathlon have some items with same ref and different ean ... ean should be really unique

#    def __init__(self, source=None, item=None):
#        if source is not None and item is not None:
#            if source == "amazon":
#                self = _amazon_init(self, item)
#        super(AffiliationItem, self).__init__()

    def __unicode__(self):
        return u"%s @ %s" % (self.item, self.store)


def _amazon_init(aff_item, amazon_item):
    amazon = Store.objects.get(url="amazon.fr")
    aff_item.store = amazon

    aff_item.object_ref = amazon_item.ASIN
    aff_item.url = amazon_item.DetailPageURL

    # Look for amazon then foreign new, then foreign used prices
    Price = None
    if amazon_item.Offers.TotalOffers > 0:
        Price = amazon_item.Offers.Offer.OfferListing.Price
    elif hasattr(amazon_item.OfferSummary, 'LowestNewPrice'):
        Price = amazon_item.OfferSummary.LowestNewPrice
    elif hasattr(amazon_item.OfferSummary, 'LowestUsedPrice'):
        Price = amazon_item.OfferSummary.LowestUsedPrice

    if Price is not None:
        if Price.CurrencyCode == "EUR":
            aff_item.currency = AffiliationItem.CURRENCIES.euro
        elif Price.CurrencyCode == "USD":
            aff_item.currency = AffiliationItem.CURRENCIES.dollar

        price_str = Price.FormattedPrice.pyval
        aff_item.price = Decimal(price_str.split(" ")[1].replace(",", "."))

    aff_item.item = Item.objects.get(pk=1)

    return aff_item
