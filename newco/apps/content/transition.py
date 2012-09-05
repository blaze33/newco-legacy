from django.db.models.signals import post_save
from django.dispatch import receiver
from items.models import Item as LegacyItem
from content.models import Item, Relation
from utils.apiservices import search_images


@receiver(post_save, sender=LegacyItem)
def sync_products(sender, instance, **kwargs):
    ''' Keep legacy items in sync with new Items of class product
    '''
    content, created = Item.objects.get_or_create(
        data__contains={'legacy_id': unicode(instance.id), 'class': 'product'})
    content.data['legacy_id'] = unicode(instance.id)
    content.data['class'] = 'product'
    content.data['name'] = instance.name
    content.save()
    return content


def add_images(request, **kwargs):
    img_order = [int(y.split('=')[1]) for y in request.POST['img_list'].split('&')]
    print img_order

    product = sync_products(LegacyItem, LegacyItem.objects.get(id=kwargs['pk']))

    album_data = {'class': 'image_set', 'name': 'main album'}
    album = product.get_items(data__contains=album_data)
    if not album:
        album = Item.objects.create(data=album_data)
    else:
        album = album[0]
    product.link(album, {'relationship': 'has'})

    r = search_images(product.data['name'])
    images = r.json['items']
    for x in img_order:
        i = images[x]
        image, created = Item.objects.get_or_create(data__contains={
            'link': i['link'],
            'class': 'image'})
        i.update(i.pop('image'))
        for k, v in i.items():
            i[k] = unicode(v)
        image.data = i
        image.data['class'] = 'image'
        image.save()
        album.link(image, {'relationship': 'contains',
            'order': unicode(img_order.index(x))})
