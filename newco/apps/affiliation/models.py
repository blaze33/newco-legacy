from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from items.models import Item

import datetime


class Currency(models.Model):
    name = models.CharField(max_length=15, verbose_name=_('name'))

    class Meta:
        abstract = True
        verbose_name = _("currency")
        verbose_name_plural = _("currencies")

    def __unicode__(self):
        return u'%s' % (self.name)


class Store(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('name'))
    url = models.URLField(max_length=200, verbose_name=_('url'))
    slug = models.SlugField(verbose_name=_('slug'), editable=False)
    last_modified = models.DateTimeField(auto_now=True,
                                         verbose_name=_('last modified'))

    class Meta:
        abstract = True
        verbose_name = _("store")

    def __unicode__(self):
        return u'%s' % (self.name)

    def save(self):
        self.slug = slugify(self.name)
        super(Store, self).save()


class AffiliationItem(models.Model):
    item = models.ForeignKey(Item)
    store = models.ForeignKey(Store, verbose_name=_('store'))
    url = models.URLField(max_length=1000, verbose_name=_('url'))
    price = models.IntegerField(default=0, verbose_name=_('price'))
    currency = models.ForeignKey(Currency, verbose_name=_('currency'),
                                           verbose_name_plural=_('currencies'))
    creation_date = models.DateTimeField(default=datetime.datetime.today(),
                                    editable=False,
                                    verbose_name=_('date created'))
    update_date = models.DateTimeField(auto_now=True,
                                    verbose_name=_('last modified'))

    class Meta:
        abstract = True
        verbose_name = _("affiliation item")

    def __unicode__(self):
        return u'%s @ %s' % (self.item, self.store)
