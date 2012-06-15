from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from items.models import Item

import datetime


class Currency(models.Model):
    name = models.CharField(max_length=15)
    
    class Meta:
        verbose_name_plural = "currencies"
    
    def __unicode__(self):
        return u'%s' % (self.name)


class Store(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField(max_length=200)
    slug = models.SlugField(verbose_name=_('Slug'), editable=False)
    last_modified = models.DateTimeField(auto_now=True,
                                         verbose_name=_('Last modified'))
    def __unicode__(self):
        return u'%s' % (self.name)


class AffiliationItem(models.Model):
    item = models.ForeignKey(Item)
    store = models.ForeignKey(Store)
    url = models.URLField(max_length=800)
    price_currency = models.ForeignKey(Currency)
    price = models.IntegerField(default=0)
    creation_date = models.DateTimeField(default=datetime.datetime.today(),
                                    editable=False,
                                    verbose_name=_('date created'))
    update_date = models.DateTimeField(auto_now=True,
                                    verbose_name=_('Last modified'))
    
    def __unicode__(self):
        return u'%s @ %s' % (self.item, self.store)
