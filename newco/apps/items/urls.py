from django.conf.urls import patterns, include, url
from items.models import Item
from items.views import ContentListView, ContentDetailView
from items.views import ContentCreateView, ContentUpdateView, ContentDeleteView

urlpatterns = patterns('',
    url(r"^$", ContentListView.as_view(model=Item), name="item_index"),
    url(r"^tag/(?P<tag_slug>[-\w]+)/$", ContentListView.as_view(model=Item),
                                        name="tagged_items"),
    url(r"^(?P<model_name>[-\w]+)/(?P<pk>\d+)/(?P<slug>[-\w]+)",
        ContentDetailView.as_view(),
        name="item_detail"),
    url(r"^add/(?P<model_name>[-\w]+)/$",
        ContentCreateView.as_view(),
        name="item_create"),
    url(r"^edit/(?P<model_name>[-\w]+)/(?P<pk>\d+)/$",
        ContentUpdateView.as_view(),
        name="item_edit"),
    url(r"^delete/(?P<model_name>[-\w]+)/(?P<pk>\d+)/$",
        ContentDeleteView.as_view(),
        name="item_delete"),
)
