from django.conf.urls.defaults import patterns, include, url
from django.views.generic import ListView

from items.models import Item
from items.views import ItemDetailView, ItemCreateView
from items.views import ItemUpdateView, ItemDeleteView

urlpatterns = patterns('',
    url(r"^$", ListView.as_view(model=Item, context_object_name="item_list"),
            name="item_index"),
    url(r"^(?P<item_id>\d+)/(?P<slug>[-\w]+)/$", ItemDetailView.as_view(),
            name="item_detail"),
    url(r"^add/item/$", ItemCreateView.as_view(),
            name="item_create"),
    url(r"^edit/item/(?P<id>\d+)/$", ItemUpdateView.as_view(),
            name="item_edit"),
    url(r"^delete/item/(?P<pk>\d+)/$", ItemDeleteView.as_view(),
            name="item_delete"),
)
