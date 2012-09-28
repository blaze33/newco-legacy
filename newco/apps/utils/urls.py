from django.conf.urls import patterns, include, url
from utils.views.search import redis_to_json, TypeaheadSearchView

urlpatterns = patterns('',
    url(r"^/redis/search", redis_to_json, name="redis"),
    url(r"^/typeahead", TypeaheadSearchView.as_view(), name="typeahead_search"),
)
