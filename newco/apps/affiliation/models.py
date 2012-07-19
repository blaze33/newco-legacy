from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from items.models import Item
from model_utils import Choices

import datetime



class Store(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('name'))
    url = models.URLField(max_length=200, verbose_name=_('url_website'))
    slug = models.SlugField(verbose_name=_('slug'), editable=False)
    last_modified = models.DateTimeField(auto_now=True,
                                         verbose_name=_('last modified'))
    url_catalog = models.URLField(max_length=200, verbose_name=_('url_catalog'))
    

    class Meta:
        verbose_name = _("store")

    def __unicode__(self):
        return u'%s' % (self.name)

    def save(self):
        self.slug = slugify(self.name)
        super(Store, self).save()


class AffiliationItem(models.Model):
    item = models.ForeignKey(Item)
    name_at_store = models.CharField(max_length=100, verbose_name=_('name at store'))
    ref_catalog = models.IntegerField(default=0, verbose_name=_('ref_catalog')) # EAN ?
    store = models.ForeignKey(Store, verbose_name=_('store'))
    url = models.URLField(max_length=600, verbose_name=_('url'))
    url_img = models.URLField(max_length=200, verbose_name=_('url img'))
    price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_('price'))
    CURRENCIES = Choices(
        (0, "euro", _("Euro")),
        (1, "dollar", _("Dollar"))
    )
    currency = models.SmallIntegerField(choices=CURRENCIES, default=CURRENCIES.euro,
                                            verbose_name=_('currency'))
    creation_date = models.DateTimeField(default=datetime.datetime.today(),
                                    editable=False,
                                    verbose_name=_('date created'))
    update_date = models.DateTimeField(auto_now=True,
                                    verbose_name=_('last modified'))

    class Meta:
        verbose_name = _("affiliation item")

    def __unicode__(self):
        return u'%s @ %s' % (self.item, self.store)
