from django.conf.urls import patterns, include, url

from dashboard.views import DashboardView


urlpatterns = patterns('',
    url(r"^$", DashboardView.as_view(), name="dash"),
    url(r"^/(?P<cat>feed|contribution|collaboration|draft|all|shopping|purchase)$", DashboardView.as_view(), name="dash"),
)
