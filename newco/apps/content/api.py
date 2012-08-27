from tastypie.resources import ModelResource
from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import DjangoAuthorization
from content.models import Item

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

class ItemResource(ModelResource):
    class Meta:
        queryset = Item.objects.all()
        resource_name = 'item'
        authorization = DjangoAuthorization()
        authentication = ApiKeyPlusWebAuthentication()
