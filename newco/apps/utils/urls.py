from django.conf.urls import patterns, include, url

from utils.views import TypeaheadSearchView

urlpatterns = patterns("",
    url(r"^", include("utils.redis.urls")),
    url(r"^/typeahead", TypeaheadSearchView.as_view(), name="search"),
)
