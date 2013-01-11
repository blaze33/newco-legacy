from django.conf.urls import patterns, include, url

from utils.redis.views import RedisView

urlpatterns = patterns("",
    url(r"^$", RedisView.as_view(), name="redis"),
    url(r"^/(?P<class>tag|item|profile)$", RedisView.as_view(), name="redis"),
)
