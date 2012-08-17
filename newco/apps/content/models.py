from django.db import models
from django_hstore import hstore
from items.models import Content
from django.utils.translation import ugettext_lazy as _

# Create your models here.
class Genre(models.Model):
    name  = models.CharField(max_length=200, verbose_name=_("name"))
    description = models.CharField(max_length=1000, verbose_name=_("description"))

    class Meta:
        verbose_name = _("genre")

    def __unicode__(self):
        return self.name


class Item(Content):
    genre = models.ForeignKey("genre")
    data = hstore.DictionaryField(db_index=True)
    objects = hstore.HStoreManager()
    context = models.ManyToManyField('self', through='Relationship',
                                     symmetrical=False,
                                     related_name='related_to')

    class Meta:
        verbose_name = _("item")

    def __unicode__(self):
        return self.genre.name


class Relationship(models.Model):
    from_item = models.ForeignKey(Item, related_name='from_item')
    to_item = models.ForeignKey(Item, related_name='to_item')
    status = models.IntegerField()

    data = hstore.DictionaryField(db_index=True)
    objects = hstore.HStoreManager()


