# -*- coding: utf-8 -*-
from decimal import Decimal

from django.db import models
from django.template.defaultfilters import slugify, truncatechars
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from babel.numbers import parse_decimal

from affiliation import CURRENCIES
from affiliation.managers import StoreManager
from items.models import Item


class Store(models.Model):
    name = models.CharField(_("name"), max_length=100)
    url = models.URLField(_("url webapp"), max_length=200)
    slug = models.SlugField(_("slug"), editable=False)
    last_modified = models.DateTimeField(_("last modified"), auto_now=True)

    objects = StoreManager()

    class Meta:
        verbose_name = _("store")

    def __unicode__(self):
        return u"%s" % (self.name)

    def save(self, **kwargs):
        self.slug = slugify(self.name)
        super(Store, self).save(**kwargs)


class AffiliationItemBase(models.Model):
    name = models.CharField(_("name at store"), max_length=200)
    store = models.ForeignKey(Store, verbose_name=_("store"))
    object_id = models.CharField(_("store object id"), max_length=30)
    ean = models.CharField(_("EAN"), max_length=30)
    url = models.URLField(_("URL"), max_length=1000)
    price = models.DecimalField(_("price"), default=0, max_digits=14,
                                decimal_places=2)
    currency = models.SmallIntegerField(_("currency"), choices=CURRENCIES,
                                        default=CURRENCIES.euro)
    creation_date = models.DateTimeField(_("date created"),
                                         default=timezone.now, editable=False)
    update_date = models.DateTimeField(_("last modified"), auto_now=True)
    img_small = models.URLField(_("small image"), max_length=1000)
    img_medium = models.URLField(_("medium image"), max_length=1000)
    img_large = models.URLField(_("large image"), max_length=1000)

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

    def same_as(self, other):
        fields = ["name", "store", "object_id", "ean", "url", "price",
                  "currency"]
        same = True
        for field in fields:
            same = same and getattr(self, field) == getattr(other, field)

        return same


class AffiliationItemCatalog(AffiliationItemBase):

    def __unicode__(self):
        return u"%s @ %s" % (self.name[:10], self.store)


class AffiliationItem(AffiliationItemBase):
    item = models.ForeignKey(Item)

    def copy_from_affcatalog(self, other):
        if other.__class__ is not AffiliationItemCatalog:
            return
        for field in self._meta.fields:
            if field.editable and not field.name in ["id", "item"]:
                value = getattr(other, field.name)
                setattr(self, field.name, value)

    class Meta:
        ordering = ["price"]
        unique_together = (("item", "store", "object_id"),)


def _amazon_init(aff_item, amazon_item):
    aff_item.store = Store.objects.get_store("Amazon")

    maxl = AffiliationItem._meta.get_field_by_name('name')[0].max_length

    aff_item.name = truncatechars(amazon_item.ItemAttributes.Title.pyval, maxl)
    aff_item.object_id = unicode(amazon_item.ASIN)
    aff_item.ean = unicode(getattr(amazon_item.ItemAttributes, "EAN", ""))
    aff_item.url = unicode(amazon_item.DetailPageURL)

    # Look for amazon then foreign new, then foreign used prices
    Price = None
    if hasattr(amazon_item, "Offers") & hasattr(amazon_item, "OfferSummary"):
        if amazon_item.Offers.TotalOffers > 0:
            if hasattr(amazon_item.Offers.Offer.OfferListing, "SalePrice"):
                Price = amazon_item.Offers.Offer.OfferListing.SalePrice
            else:
                Price = amazon_item.Offers.Offer.OfferListing.Price
        elif hasattr(amazon_item.OfferSummary, "LowestNewPrice"):
            Price = amazon_item.OfferSummary.LowestNewPrice
        elif hasattr(amazon_item.OfferSummary, "LowestUsedPrice"):
            Price = amazon_item.OfferSummary.LowestUsedPrice

    if Price is not None:
        if Price.CurrencyCode == "EUR":
            aff_item.currency = CURRENCIES.euro
        elif Price.CurrencyCode == "USD":
            aff_item.currency = CURRENCIES.dollar

        price_str = Price.FormattedPrice.pyval.split(" ")
        # fr_FR locale won't recognize the thousand dot separator !?!
        price = parse_decimal(price_str[1], locale="de")

        aff_item.price = Decimal(price).quantize(Decimal('.01'))

    if hasattr(amazon_item, "SmallImage"):
        aff_item.img_small = unicode(amazon_item.SmallImage.URL)
    if hasattr(amazon_item, "MediumImage"):
        aff_item.img_medium = unicode(amazon_item.MediumImage.URL)
    if hasattr(amazon_item, "LargeImage"):
        aff_item.img_large = unicode(amazon_item.LargeImage.URL)

    return aff_item


def _decathlon_init(aff_item, decathlon_item):
    aff_item.store = Store.objects.get_store("Decathlon")
    max_chars = AffiliationItem._meta.get_field_by_name('name')[0].max_length

    for key, value in decathlon_item.items():
        if key == "Prix":
            price = Decimal(value.replace(",", ".")).quantize(Decimal('.01'))
        elif key == "Prix barré":
            price_2 = Decimal(value.replace(",", ".")).quantize(Decimal('.01'))
        elif key == "Monnaie":
            currency = unicode(value, "utf-8")
        elif key == "Url":
            aff_item.url = unicode(value)
        elif key == "EAN":
            aff_item.ean = unicode(value)
        elif key == "Nom":
            aff_item.name = truncatechars(unicode(value, "utf-8"), max_chars)
        elif key == "Id produit":
            aff_item.object_id = unicode(value)
        elif key == "Url image petite":
            aff_item.img_small = unicode(value)
        elif key == "Url image moyenne":
            aff_item.img_medium = unicode(value)
        elif key == "Url image grande":
            aff_item.img_large = unicode(value)

    aff_item.price = price if price and price < price_2 else price_2

    if currency == u"€":
        aff_item.currency = CURRENCIES.euro
    else:
        aff_item.currency = CURRENCIES.dollar

    return aff_item
