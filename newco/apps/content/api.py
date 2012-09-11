from tastypie.resources import ModelResource
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie import fields
from tastypie.fields import ApiField
from content.models import Item, Relation

class ApiKeyPlusWebAuthentication(ApiKeyAuthentication):
    def is_authenticated(self, request, **kwargs):
        if request.user.is_authenticated():
            return True

        return super(ApiKeyPlusWebAuthentication, self).is_authenticated(request, **kwargs)

    def get_identifier(self, request):
        if request.user.is_authenticated():
            return request.user.username
        else:
            return super(ApiKeyPlusWebAuthentication, self).get_identifier(request)

class BaseResource(ModelResource):
    data = fields.DictField(attribute='data')

    class Meta:
        abstract = True

class ItemResource(BaseResource):
    class Meta:
        queryset = Item.objects.all()
        resource_name = 'item'
        authorization = DjangoAuthorization()
        authentication = ApiKeyPlusWebAuthentication()
        include_absolute_url = True


class RelationResource(BaseResource):
    from_item = fields.ToOneField( ItemResource, 'from_item')
    to_item = fields.ToOneField( ItemResource, 'to_item')

    class Meta:
        queryset = Relation.objects.all()
        resource_name = 'relation'
        authorization = DjangoAuthorization()
        authentication = ApiKeyPlusWebAuthentication()
        include_absolute_url = True