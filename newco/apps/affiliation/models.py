# -*- coding: utf-8 -*-
import decimal
import re

from django.db import models
from django.template.defaultfilters import slugify, truncatechars
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from babel.numbers import parse_decimal

from affiliation import CURRENCIES, AVAILABILITY_PATTERNS
from affiliation.managers import StoreManager
from items.models import Item

NAME_MAX_LENGTH = 200
ROUND = decimal.Decimal(".01")


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


class AffiliationItem(models.Model):
    name = models.CharField(_("name at store"), max_length=NAME_MAX_LENGTH)
    store = models.ForeignKey(Store, verbose_name=_("store"))
    object_id = models.CharField(_("store object id"), max_length=30)
    ean = models.CharField(_("EAN"), max_length=30)
    url = models.URLField(_("URL"), max_length=1000)
    price = models.DecimalField(_("price"), default=0, max_digits=14,
                                decimal_places=2)
    currency = models.SmallIntegerField(_("currency"), choices=CURRENCIES,
                                        default=CURRENCIES.euro)
    shipping_price = models.DecimalField(_("shipping_price"), default=-1,
                                         max_digits=14, decimal_places=2)
    availability = models.CharField(_("availability"), max_length=50,
                                    default="see site")
    creation_date = models.DateTimeField(_("date created"),
                                         default=timezone.now, editable=False)
    update_date = models.DateTimeField(_("last modified"), auto_now=True)
    img_small = models.URLField(_("small image"), max_length=1000)
    img_medium = models.URLField(_("medium image"), max_length=1000)
    img_large = models.URLField(_("large image"), max_length=1000)

    item = models.ForeignKey(Item, null=True, blank=True)

    class Meta:
        verbose_name = _("affiliation item")
        unique_together = (('store', 'object_id'),)

    def __unicode__(self):
        return u"%s @ %s" % (self.name[:10], self.store)

    def store_init(self, store, item):
        if store.__class__ is Store and item is not None:
            if store.name == "Amazon":
                self = _amazon_init(self, item)
            elif store.name == "Decathlon":
                self = _decathlon_init(self, item)
            self.store = store

    def same_as(self, other):
        fields = ["name", "store", "object_id", "ean", "url", "price",
                  "currency", "availability", "shipping_price"]
        same = True
        for field in fields:
            same = same and getattr(self, field) == getattr(other, field)

        return same


def _amazon_init(aff_item, amazon_item):
    CURRENCY_TABLE = {"EUR": CURRENCIES.euro, "USD": CURRENCIES.dollar,
                      "GBP": CURRENCIES.pound}

    aff_item.name = truncatechars(amazon_item.ItemAttributes.Title.pyval,
                                  NAME_MAX_LENGTH)
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
        aff_item.currency = CURRENCY_TABLE.get(Price.CurrencyCode,
                                               CURRENCIES.euro)

        price_str = Price.FormattedPrice.pyval.split(" ")
        # fr_FR locale won't recognize the thousand dot separator !?!
        price = parse_decimal(price_str[1], locale="de")

        aff_item.price = decimal.Decimal(price).quantize(ROUND)

    if hasattr(amazon_item, "SmallImage"):
        aff_item.img_small = unicode(amazon_item.SmallImage.URL)
    if hasattr(amazon_item, "MediumImage"):
        aff_item.img_medium = unicode(amazon_item.MediumImage.URL)
    if hasattr(amazon_item, "LargeImage"):
        aff_item.img_large = unicode(amazon_item.LargeImage.URL)

    return aff_item


def _decathlon_init(aff_item, decathlon_item):
    MATCHING_TABLE = {
        "Url": "url",
        "EAN": "ean",
        "Id produit": "object_id",
        "Url image petite": "img_small",
        "Url image moyenne": "img_medium",
        "Url image grande": "img_large"
    }

    CURRENCY_TABLE = {u"€": CURRENCIES.euro, u"$": CURRENCIES.dollar,
                      u"£": CURRENCIES.pound}

    DECATHLON_AVAILABILITY_PATTERN = "(?P<days>\d*)\s?jours"
    EXACT_PATTERN = AVAILABILITY_PATTERNS["exact"]

    ROUND = decimal.Decimal(".01")

    for key, value in decathlon_item.items():
        if key == "Prix":
            parsed_price = parse_decimal(value, locale="fr")
            price = decimal.Decimal(parsed_price).quantize(ROUND)
        elif key == "Prix barré":
            parsed_price = parse_decimal(value, locale="fr")
            price_2 = decimal.Decimal(parsed_price).quantize(ROUND)
        elif key == "Monnaie":
            currency = unicode(value, "utf-8")
            aff_item.currency = CURRENCY_TABLE.get(currency, None)
        elif key == "Frais de port":
            parsed_price = parse_decimal(value, locale="fr")
            aff_item.shipping_price = decimal.Decimal(
                parsed_price).quantize(ROUND)
        elif key == "Nom":
            aff_item.name = truncatechars(unicode(value, "utf-8"),
                                          NAME_MAX_LENGTH)
        elif key == "Disponibilité":
            match = re.match(DECATHLON_AVAILABILITY_PATTERN, value)
            if match is not None:
                days = match.groups("days")[0]
                if days:
                    aff_item.availability = EXACT_PATTERN.format(
                        value=days, unit="D")
                else:
                    aff_item.availability = "in stock"
        elif key in MATCHING_TABLE:
            setattr(aff_item, MATCHING_TABLE[key], unicode(value))

    aff_item.price = price if price and price < price_2 else price_2

    return aff_item
