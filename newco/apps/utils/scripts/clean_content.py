# coding: utf-8
from django.conf import settings
print "Using " + settings.DATABASES["default"]["NAME"] + """ database.
node products with deleted legacy items are deleted.
"""
from content.models import GraphQuery, Item as cItem
from items.models import Item


def clean_nodes_products():
    ids = map(lambda x: int(x.data['legacy_id']), cItem.objects.hfilter({'_class': 'product'}))
    legacy_ids = map(lambda x: x.id, Item.objects.filter(pk__in=ids))
    deleted_ids = [i for i in ids if i not in legacy_ids]

    old = [x for x in cItem.objects.hfilter({'_class': 'product'}).hselect(['legacy_id'])
           if int(x.legacy_id) in deleted_ids]
    print 'Those items were already deleted:', old, '\n'

    n_img, n_album = 0, 0
    for i in old:
        if i.successors.all():
            n_album += i.successors.count()
            i.successors.all().delete()
        i.delete()

    n_img = GraphQuery().isolated().count()
    GraphQuery().isolated().delete()

    print 2 * n_album + n_img, 'nodes deleted:', \
        n_album, 'product nodes,', \
        n_album, 'album nodes,', \
        n_img, 'image nodes'
    print 'many relations deleted'

if __name__ == "__main__":
    clean_nodes_products()
