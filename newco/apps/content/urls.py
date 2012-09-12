from django.conf.urls import patterns, include, url
from content.models import Item
from content.views import ContentListView, ContentDetailView
from content.views import ContentCreateView, ContentUpdateView, ContentDeleteView

urlpatterns = patterns('',
    url(r"^$", ContentListView.as_view(model=Item), name="content_index"),
    url(r"^(?P<model_name>[-\w]+)/(?P<pk>\d+)/(?P<slug>[-\w]*)",
        ContentDetailView.as_view(),
        name="content_detail"),
    url(r"^(?P<model_name>[-\w]+)/$", ContentListView.as_view(), name="model_index"),
    url(r"^add/(?P<model_name>[-\w]+)/$",
        ContentCreateView.as_view(),
        name="content_create"),
    url(r"^edit/(?P<model_name>[-\w]+)/(?P<pk>\d+)/$",
        ContentUpdateView.as_view(),
        name="content_edit"),
    url(r"^delete/(?P<model_name>[-\w]+)/(?P<pk>\d+)/$",
        ContentDeleteView.as_view(),
        name="content_delete"),
)