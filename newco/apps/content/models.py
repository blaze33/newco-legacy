from django.db import models
from django.db.models import permalink
from django_extensions.db.models import TimeStampedModel
from django_hstore import hstore
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from voting.models import Vote


class VoteModel(TimeStampedModel):
    """ VoteModel
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
        super(VoteModel, self).delete()


class BaseModel(VoteModel):
    """ BaseModel
    An abstract base class with timestamps and votes.
    Stores data with HStore.
    """
    data = hstore.DictionaryField(db_index=True)
    objects = hstore.HStoreManager()

    class Meta:
        abstract = True

    def get(self, key):
        try:
            return self.data[key]
        except:
            return None

    @permalink
    def get_absolute_url(self):
        slug = self.get('slug')
        return ('content_detail', None, {
            "model_name": self.__class__.__name__,
            "pk": self.id, "slug": slug})


class Item(BaseModel):
    """ Item
    A generic class to store any kind of object.
    """
    context = models.ManyToManyField('self', through='Relation',
                                     symmetrical=False,
                                     related_name='related_to')

    class Meta:
        verbose_name = _("item")

    def get_items(self):
        return self.context.filter(
            to_item__from_item=self)

    def get_relations(self):
        return Relation.objects.filter(
            from_item=self)

    def get_related_items(self):
        return self.related_to.filter(
            from_item__to_item=self)

    def get_related_relations(self):
        return Relation.objects.filter(
            to_item=self)

    def __unicode__(self):
        return unicode(self.get('name'))


class Relation(BaseModel):
    """ Relation
    A class describing a relation between two items.
    """
    from_item = models.ForeignKey(Item, related_name='from_item')
    to_item = models.ForeignKey(Item, related_name='to_item')

    def __unicode__(self):
        return "%s %s %s" % (self.from_item.get('name'),
                             self.get('relationship'),
                             self.to_item.get('name'))
