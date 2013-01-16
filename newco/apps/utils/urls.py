from django.conf.urls import patterns, include, url

from utils.views.search import TypeaheadSearchView

urlpatterns = patterns("",
    url(r"^/redis", include("utils.redis.urls")),
    url(r"^/typeahead", TypeaheadSearchView.as_view(), name="search"),
)
