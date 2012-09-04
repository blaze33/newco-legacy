from django.db.models.signals import post_save
from django.dispatch import receiver
from items.models import Item as LegacyItem
from content.models import Item


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
