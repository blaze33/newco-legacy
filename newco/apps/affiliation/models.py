from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from taggit.managers import TaggableManager

from idios.models import ProfileBase

from items.models import Item

import datetime


class Store(models.Model):
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=100)
    slug = models.SlugField(verbose_name=_('Slug'), editable=False)
    last_modified = models.DateTimeField(auto_now=True,
                                         verbose_name=_('Last modified'))


class Affiliation_Item_Store(models.Model):
    item = models.ManyToManyField(Item)
    store = models.ForeignKey(Store)
    url = models.CharField(max_length=400)
    creation_date = models.DateTimeField(default=datetime.datetime.today(),
                                    editable=False,
                                    verbose_name=_('date created'))
    update_date = models.DateTimeField(auto_now=True,
                                    verbose_name=_('Last modified'))
