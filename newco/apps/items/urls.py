from django.conf.urls import patterns, include, url

from items.views import (
    ContentListView, ContentDetailView,
    ContentCreateView, ContentUpdateView, ContentDeleteView,
    TopCategoriesView
)

urlpatterns = patterns("",
    url(r"^tag/(?P<tag_slug>[-\w]+)$", ContentListView.as_view(),
        name="tagged_items"),
    url(r"^tag/(?P<tag_slug>[-\w]+)/(?P<cat>products|questions)$",
        ContentListView.as_view(), name="tagged_items"),
    url(r"^(?P<model_name>[-\w]+)/(?P<pk>\d+)/(?P<slug>[-\w./]*)",
        ContentDetailView.as_view(),
        name="item_detail"),
    url(r"^add/(?P<model_name>[-\w]+)$",
        ContentCreateView.as_view(),
        name="item_create"),
    url(r"^edit/(?P<model_name>[-\w]+)/(?P<pk>\d+)$",
        ContentUpdateView.as_view(),
        name="item_edit"),
    url(r"^delete/(?P<model_name>[-\w]+)/(?P<pk>\d+)$",
        ContentDeleteView.as_view(),
        name="item_delete"),
    url(r"^(?P<format>json)/top_categories$",
        TopCategoriesView.as_view(), {'format': 'json'},
        name="top_categories_json"),
)
