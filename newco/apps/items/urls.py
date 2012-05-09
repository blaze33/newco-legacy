from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template
from django.views.generic import ListView, CreateView
from items.models import Item
from items.views import ItemCreateView

urlpatterns = patterns('',
    url(r"^$", ListView.as_view(
        model=Item,
        context_object_name="item_list",
        ), name="item-index"),
    url(r"^(?P<item_id>\d+)/$", 'detail', name="item-detail"),
    url(r"^add/$", ItemCreateView.as_view(), name="item-create"),
)
