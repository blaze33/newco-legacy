from django.db.models import Count

from django_hstore.managers import HStoreManager
from django_hstore.query import HStoreQuerySet, select_query
from django_hstore.fields import HStoreDescriptor


class QuerySet(HStoreQuerySet):

    def __init__(self, model=None, query=None, using=None):
        super(QuerySet, self).__init__(model, query, using)
        d = self.model.__dict__
        hfields = [x for x in d if type(d[x]) == HStoreDescriptor]
        if len(hfields) > 0:  # TODO: solve multiple hstore fields case.
            self.hfield = hfields[0]

    @select_query
    def hselect(self, query, keys):
        """
        Returns a ValuesQuerySet with the keys corresponding
        to keys of the specified hstore.
        """
        table = self.model._meta.db_table
        extra_select = dict([(k,
                              "{0}.{1} -> %s".format(table, self.hfield)
                              ) for k in keys])
        clone = self._clone()
        clone.query.add_extra(extra_select, keys, None, None, None, None)
        return clone

    @select_query
    def hfilter(self, query, params):
        return self.filter(**{'{0}__contains'.format(self.hfield): params})

    @select_query
    def hkeys(self, query):
        keys = self.extra(select=dict(key='skeys({0})'.format(self.hfield))) \
                   .values('key').annotate(Count('id')) \
                   .order_by('-id__count', 'key')
        return tuple((k['key'], k['id__count']) for k in keys)

    @select_query
    def hvalues(self, query, key):
        values = self.hselect([key]) \
                     .values(key).annotate(Count('id')) \
                     .order_by('-id__count', key)
        return tuple((v[key], v['id__count']) for v in values)

    @select_query
    def isolated(self, query):
        return self.filter(links__isnull=True, inlinks__isnull=True)


class Manager(HStoreManager):
    """Object manager which enables additional hstore features."""

    def get_query_set(self):
        return QuerySet(self.model, using=self._db)

    def hselect(self, keys):
        return self.get_query_set().hselect(keys)

    def hfilter(self, params):
        return self.get_query_set().hfilter(params)

    def hkeys(self):
        return self.get_query_set().hkeys()

    def hvalues(self, key):
        return self.get_query_set().hvalues(key)

    def isolated(self):
        return self.get_query_set().isolated()
