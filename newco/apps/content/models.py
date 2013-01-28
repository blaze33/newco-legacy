from django.db import models
from django.db.models import permalink, Count
from django.utils.translation import ugettext_lazy as _

from django.contrib.contenttypes import generic

from django_extensions.db.models import TimeStampedModel
from django_hstore import hstore

from content.manager import Manager
from utils.voting import Vote


class GraphQuery(object):

    def __get__(self, instance, owner):
        self.item = instance
        return self

    def __getattr__(self, name):
        return self.item.successors.hfilter({'_class': name})

    def _get_class(self, klass):
        return klass if klass else Item

    def values(self, key, klass=None):
        klass = self._get_class(klass)
        return klass.objects.hvalues(key)

    def keys(self, klass=None):
        klass = self._get_class(klass)
        return klass.objects.hkeys()

    def isolated(self, klass=None):
        klass = self._get_class(klass)
        return klass.objects.isolated()

    def get_image(self):
        try:
            q = Item.objects.filter(inlinks__data__contains={'order': '0'},
                inlinks__from_item__inlinks__from_item_id=self.item.id)
            return q[0]
        except IndexError:
            return None

    def get_images(self, ids=None):
        ids = ids if ids else [self.item.id]
        q = Item.objects.filter(inlinks__data__contains={'order': '0'},
            inlinks__from_item__inlinks__from_item_id__in=ids
            )
        return q


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
    objects = Manager()

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
    graph = GraphQuery()
    initial = {'data': {'_class': ''}}

    class Meta:
        verbose_name = _("item")

    def __unicode__(self):
        name = self.get("name")
        if name:
            return unicode(name)
        else:
            return unicode("<{0}: {1}>".format(self.get("class"), self.id))

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

    initial = {'data': {}}

    def __unicode__(self):
        return "%s %s %s" % (self.from_item.get('name'),
                             self.get('relationship'),
                             self.to_item.get('name'))
