from django_extensions.db.models import TimeStampedModel
from django_hstore import hstore
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from voting.models import Vote


class BaseModel(TimeStampedModel):
    """ BaseModel
    An abstract base class with timestamps and votes.
    """
    votes = generic.GenericRelation(Vote)

    class Meta:
        abstract = True

    def delete(self):
        try:
            self.votes.all().delete()
        except:
            pass
        super(Content, self).delete()


class Item(BaseModel):
    """ Item
    A generic class to store any kind of object with an HStore to store data.
    context list the related items.
    """
    data = hstore.DictionaryField(db_index=True)
    objects = hstore.HStoreManager()
    context = models.ManyToManyField('self', through='Relation',
                                     symmetrical=False,
                                     related_name='related_to')

    class Meta:
        verbose_name = _("item")

    def get(self, key):
        try:
            return self.data[key]
        except:
            return None

    def __unicode__(self):
        return self.get('name')


class Relation(BaseModel):
    """ Relation
    A class describing a relation between two items.
    """
    from_item = models.ForeignKey(Item, related_name='from_item')
    to_item = models.ForeignKey(Item, related_name='to_item')

    data = hstore.DictionaryField(db_index=True)
    objects = hstore.HStoreManager()
