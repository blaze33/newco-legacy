from django.conf.urls.defaults import patterns, include, url
from django.views.generic import ListView

from items.models import Item
from items.views import ItemDetailView, ContentDeleteView
from items.views import ContentCreateView, ContentUpdateView

urlpatterns = patterns('',
    url(r"^$", ListView.as_view(model=Item, context_object_name="item_list"),
            name="item_index"),
    url(r"^(?P<item_id>\d+)/(?P<slug>[-\w]+)/$", ItemDetailView.as_view(),
            name="item_detail"),
    url(r"^delete/(?P<model_name>[-\w]+)/(?P<pk>\d+)/$", ContentDeleteView.as_view(),
            name="item_delete"),
    url(r"^edit/(?P<model_name>[-\w]+)/(?P<pk>\d+)/$", ContentUpdateView.as_view(),
            name="item_edit"),
    url(r"^add/(?P<model_name>[-\w]+)/$", ContentCreateView.as_view(),
            name="item_create"),
)
