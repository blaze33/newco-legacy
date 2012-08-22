from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from decimal import Decimal

from model_utils import Choices

from items.models import Item


class Store(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("name"))
    url = models.URLField(max_length=200, verbose_name=_("url webapp"))
    slug = models.SlugField(verbose_name=_("slug"), editable=False)
    last_modified = models.DateTimeField(auto_now=True,
                                         verbose_name=_("last modified"))

    class Meta:
        verbose_name = _("store")

    def __unicode__(self):
        return u"%s" % (self.name)

    def save(self, **kwargs):
        self.slug = slugify(self.name)
        super(Store, self).save(**kwargs)


class AffiliationItemBase(models.Model):
    CURRENCIES = Choices(
        (0, "euro", _("Euro")),
        (1, "dollar", _("Dollar")),
        (2, "pound", _("Pound"))
    )

    name = models.CharField(max_length=200, verbose_name=_("name at store"))
    store = models.ForeignKey(Store, verbose_name=_("store"))
    object_id = models.CharField(max_length=30,
                                        verbose_name=_("store object id"))
    ean = models.CharField(max_length=30, verbose_name=_("EAN"))
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
    img_small = models.URLField(max_length=1000,
                                        verbose_name=_("small image"))
    img_medium = models.URLField(max_length=1000,
                                        verbose_name=_("medium image"))
    img_large = models.URLField(max_length=1000,
                                        verbose_name=_("large image"))

    class Meta:
        abstract = True
        verbose_name = _("affiliation item")
        unique_together = (('store', 'object_id'),)

    def __unicode__(self):
        return u"%s @ %s" % (self.item, self.store)

    def store_init(self, source, item):
        if source is not None and item is not None:
            if source == "amazon":
                self = _amazon_init(self, item)
            elif source == "decathlon":
                self = _decathlon_init(self, item)

    def identical(self, other):
        identical = self.name == other.name
        identical = identical and self.store == other.store
        identical = identical and self.object_id == other.object_id
        identical = identical and self.ean == other.ean
        identical = identical and self.url == other.url
        identical = identical and self.price == other.price
        identical = identical and self.currency == other.currency

        return identical


class AffiliationItemCatalog(AffiliationItemBase):

    def __unicode__(self):
        return u"%s @ %s" % (self.name[:10], self.store)


class AffiliationItem(AffiliationItemBase):
    item = models.ForeignKey(Item)

    def copy_from_affcatalog(self, other):
        self.name = other.name
        self.store = other.store
        self.object_id = other.object_id
        self.ean = other.ean
        self.url = other.url
        self.price = other.price
        self.currency = other.currency
        self.img_small = other.img_small
        self.img_medium = other.img_medium
        self.img_large = other.img_large

    class Meta:
        unique_together = (("item", "store", "object_id"),)


def _amazon_init(aff_item, amazon_item):
    amazon, created = Store.objects.get_or_create(
        name="Amazon", url="http://www.amazon.fr"
    )
    aff_item.store = amazon

    aff_item.name = amazon_item.ItemAttributes.Title.pyval
    aff_item.object_id = unicode(amazon_item.ASIN)
    aff_item.ean = unicode(getattr(amazon_item.ItemAttributes, "EAN", ""))
    aff_item.url = unicode(amazon_item.DetailPageURL)

    # Look for amazon then foreign new, then foreign used prices
    Price = None
    if hasattr(amazon_item, "Offers") & hasattr(amazon_item, "OfferSummary"):
        if amazon_item.Offers.TotalOffers > 0:
            Price = amazon_item.Offers.Offer.OfferListing.Price
        elif hasattr(amazon_item.OfferSummary, "LowestNewPrice"):
            Price = amazon_item.OfferSummary.LowestNewPrice
        elif hasattr(amazon_item.OfferSummary, "LowestUsedPrice"):
            Price = amazon_item.OfferSummary.LowestUsedPrice

    if Price is not None:
        if Price.CurrencyCode == "EUR":
            aff_item.currency = AffiliationItem.CURRENCIES.euro
        elif Price.CurrencyCode == "USD":
            aff_item.currency = AffiliationItem.CURRENCIES.dollar

        price_str = Price.FormattedPrice.pyval
        aff_item.price = Decimal(
            price_str.split(" ")[1].replace(",", ".")).quantize(Decimal('.01'))

    if hasattr(amazon_item, "SmallImage"):
        aff_item.img_small = unicode(amazon_item.SmallImage.URL)
    if hasattr(amazon_item, "MediumImage"):
        aff_item.img_medium = unicode(amazon_item.MediumImage.URL)
    if hasattr(amazon_item, "LargeImage"):
        aff_item.img_large = unicode(amazon_item.LargeImage.URL)

    return aff_item


def _decathlon_init(aff_item, decathlon_item):
    decathlon, created = Store.objects.get_or_create(
        name="Decathlon", url="http://www.decathlon.fr"
    )
    aff_item.store = decathlon

    for key, value in decathlon_item.items():
        if key == "Prix":
            aff_item.price = Decimal(value.replace(",", ".")).quantize(
                                                                Decimal('.01'))
        elif key == "Url":
            aff_item.url = unicode(value)
        elif key == "EAN":
            aff_item.ean = unicode(value)
        elif key == "Nom":
            aff_item.name = unicode(value, "utf-8")
        elif key == "Id produit":
            aff_item.object_id = unicode(value)
        elif key == "Url image petite":
            aff_item.img_small = unicode(value)
        elif key == "Url image moyenne":
            aff_item.img_medium = unicode(value)
        elif key == "Url image grande":
            aff_item.img_large = unicode(value)

    return aff_item
