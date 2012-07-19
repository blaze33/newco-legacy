from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

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
    store_id = models.CharField(max_length=30, verbose_name=_("store object id"))
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

    def __unicode__(self):
        return u"%s @ %s" % (self.item, self.store)
