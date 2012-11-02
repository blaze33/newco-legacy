from django.conf.urls import patterns, include, url
from utils.views.search import RedisView, TypeaheadSearchView

urlpatterns = patterns('',
    url(r"^/redis$", RedisView.as_view(), name="redis"),
    url(r"^/redis/(?P<redis_cat>tags|items|profiles|questions)$", RedisView.as_view(), name="redis"),
    url(r"^/typeahead", TypeaheadSearchView.as_view(), name="search"),
)
