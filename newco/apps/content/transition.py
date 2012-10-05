from django.db.models.signals import post_save
from django.dispatch import receiver
from items.models import Item as LegacyItem
from content.models import Item
from utils.apiservices import search_images


@receiver(post_save, sender=LegacyItem)
def sync_products(sender, instance, **kwargs):
    ''' Keep legacy items in sync with new Items of class product
    '''
    content, created = Item.objects.get_or_create(
        data__contains={'legacy_id': unicode(instance.id), '_class': 'product'})
    if not created and content.data['name'] == instance.name:
        return content
    content.data.update({'legacy_id': unicode(instance.id),
                         '_class': 'product',
                         'name': instance.name})
    content.save()
    return content


def add_images(request, **kwargs):

    legacy_product = LegacyItem.objects.get(id=kwargs['pk'])
    product = sync_products(LegacyItem, legacy_product)

    album_data = {'_class': 'image_set', 'name': 'main album'}
    album = product.successors.filter(data__contains=album_data)
    if not album:
        album = Item.objects.create(data=album_data)
        images = []
        product.link_to(album, {'relationship': 'has'})
    else:
        album = album[0]
        images = get_album(legacy_product)
        album.successors.clear()

    if not images:
        images = search_images(product.data['name'])
    if 'img_list' not in request.POST or len(request.POST['img_list']) < 1:
        album.delete()
        return
    img_order = [int(y.split('=')[1]) for y in request.POST['img_list'].split('&')]
    id_order = []
    for x in img_order:
        i = images[x]
        image, created = Item.objects.get_or_create(data__contains={
            'link': i['link'],
            '_class': 'image'})
        for k, v in i.items():
            i[k] = unicode(v)
        image.data = i
        image.data['_class'] = 'image'
        image.save()
        album.link_to(image, {'relationship': 'contains',
            'order': unicode(img_order.index(x))})
        id_order.append(image.id)
    album.data['id_order'] = unicode(id_order)
    album.save()


def get_album(instance):
    item = sync_products(LegacyItem, instance)
    album = item.successors.filter(data__contains={'_class': 'image_set'})
    if not album:
        return []
    ids = [int(x) for x in album[0].data['id_order'].strip('[]').split(',')]
    images = Item.objects.filter(pk__in=ids)
    images = sorted(images, key=lambda k: ids.index(k.id))
    json = [i.data for i in images]

    return json
