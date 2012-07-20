from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from decimal import Decimal

from model_utils import Choices

from items.models import Item


class Store(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("name"))
    url = models.URLField(max_length=200, verbose_name=_("url"))
    slug = models.SlugField(verbose_name=_("slug"), editable=False)
    last_modified = models.DateTimeField(auto_now=True,
                                         verbose_name=_("last modified"))

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
    store = models.ForeignKey(Store, verbose_name=_("store"))
    object_id = models.CharField(max_length=30,
                                        verbose_name=_("store object id"))
    url = models.URLField(max_length=1000, verbose_name=_("url"))
    price = models.DecimalField(default=0, max_digits=14, decimal_places=2,
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
        unique_together = (('store', 'object_id'),)

    def __init__(self, source=None, item=None):
        if source is not None and item is not None:
            if source == "amazon":
                self = _amazon_init(self, item)
        super(AffiliationItem, self).__init__()

    def __unicode__(self):
        return u"%s @ %s" % (self.item, self.store)


def _amazon_init(aff_item, amazon_item):
    amazon = Store.objects.get(url="amazon.fr")
    aff_item.store = amazon

    aff_item.object_id = amazon_item.ASIN
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
