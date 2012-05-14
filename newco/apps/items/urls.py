from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template
from django.views.generic import UpdateView, ListView, CreateView, DetailView
from items.models import Item
from items.views import *

urlpatterns = patterns('',
    url(r"^$", ListView.as_view(
        model=Item,
        context_object_name="item_list",
        ), name="item_index"),
    url(r"^(?P<item_id>\d+)/(?P<slug>[-\w]+)/$", ItemDetailView.as_view(
        ), name="item_detail"),
    url(r"^add/(?P<model_name>[-\w]+)/$", ContentCreateView.as_view(), name="item_create"),
    url(r"^edit/item/(?P<id>\d+)/$", ItemUpdateView.as_view(), name="item_edit"),
)
