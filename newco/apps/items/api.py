from tastypie.resources import ModelResource
from tastypie.authorization import DjangoAuthorization
from items.models import Item


class ItemResource(ModelResource):
    class Meta:
        queryset = Item.objects.all()
        resource_name = 'item'
        authorization = DjangoAuthorization()
