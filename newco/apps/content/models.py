from django.db import models
from django.db.models import permalink
from django.utils.translation import ugettext_lazy as _

from django.contrib.contenttypes import generic

from django_extensions.db.models import TimeStampedModel
from django_hstore import hstore
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
    successors = models.ManyToManyField('self', through='Relation',
                                     symmetrical=False,
                                     related_name='predecessors')

    class Meta:
        verbose_name = _("item")

    def __unicode__(self):
        name = self.get("name")
        if name:
            return unicode(name)
        else:
            return unicode("<%s: %d>" % (self.get("class"), self.id))

    def link_to(self, item, data):
        if 'relationship' in data:
            test = {'relationship': data['relationship']}
        else:
            test = {}
        relation, created = Relation.objects.get_or_create(
            from_item=self,
            to_item=item,
            data__contains=test)
        relation.data = data
        relation.save()
        return relation


class Relation(BaseModel):
    """ Relation
    A class describing a relation between two items.
    """
    from_item = models.ForeignKey(Item, related_name='links')
    to_item = models.ForeignKey(Item, related_name='inlinks')

    def __unicode__(self):
        return "%s %s %s" % (self.from_item.get('name'),
                             self.get('relationship'),
                             self.to_item.get('name'))

import content.transition
