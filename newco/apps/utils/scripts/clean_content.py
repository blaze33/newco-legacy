# coding: utf-8
from django.conf import settings
print "Using " + settings.DATABASES["default"]["NAME"] + """ database.
node products with deleted legacy items are deleted.
"""
from content.models import Item as cItem
from items.models import Item

ids = map(lambda x: int(x.data['legacy_id']), cItem.objects.hfilter({'_class': 'product'}))
exids = map(lambda x: x.id, Item.objects.filter(pk__in=ids))
id666 = [i for i in ids if i not in exids]


def deleted_legacy(x):
    global id666
    return True if int(x.legacy_id) in id666 else False

old = filter(deleted_legacy, cItem.objects.hfilter({'_class': 'product'}).hselect(['legacy_id']))
print 'Those items were already deleted:', old

n_img, n_album = 0, 0
for i in old:
    if i.successors.all():
        n_img += i.successors.all()[0].successors.all().count()
        n_album += 1
        i.successors.all()[0].successors.all().delete()
        i.successors.all().delete()
    i.delete()

print 2 * n_album + n_img, 'nodes deleted:'
print n_album, 'product nodes,', n_album, 'album nodes,', n_img, 'image nodes'
print 'many relations deleted'
