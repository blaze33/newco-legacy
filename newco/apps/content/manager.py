from django_hstore.managers import HStoreManager
from django_hstore.query import HStoreQuerySet, select_query


class QuerySet(HStoreQuerySet):

    @select_query
    def hselect(self, query, attr, keys):
        """
        Returns a ValuesQuerySet with the keys corresponding
        to keys of the specified hstore.
        """
        table = self.model._meta.db_table
        extra_select = dict([(k,
                              "{0}.{1} -> %s".format(table, attr)
                              ) for k in keys])
        clone = self._clone()
        clone.query.add_extra(extra_select, keys, None, None, None, None)
        return clone


class Manager(HStoreManager):
    """Object manager which enables additional hstore features."""

    def get_query_set(self):
        return QuerySet(self.model, using=self._db)

    def hselect(self, attr, keys, **params):
        return self.filter(**params).hselect(attr, keys)
