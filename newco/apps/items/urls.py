from django.conf.urls.defaults import patterns, include, url
from items.models import Item
from items.views import ContentListView, ContentDetailView, ContentCreateView
from items.views import ContentUpdateView, ContentDeleteView

urlpatterns = patterns('',
    url(r"^$", ContentListView.as_view(model=Item), name="item_index"),
    url(r"^(?P<model_name>[-\w]+)/(?P<pk>\d+)/(?P<slug>[-\w]+)/$",
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
