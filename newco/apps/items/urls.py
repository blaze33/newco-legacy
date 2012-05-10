from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template
from django.views.generic import ListView, CreateView, DetailView
from items.models import Item
from items.views import ItemCreateView, ItemDetailView

urlpatterns = patterns('',
    url(r"^$", ListView.as_view(
        model=Item,
        context_object_name="item_list",
        ), name="item_index"),
    url(r"^(?P<item_id>\d+)/(?P<slug>[-\w]+)/$", ItemDetailView.as_view(
        ), name="item_detail"),
    url(r"^add/$", CreateView.as_view(model=Item), name="item_create"),
)
