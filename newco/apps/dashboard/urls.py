from django.conf.urls import patterns, include, url

from dashboard.views import DashboardView
from dashboard.views import ProfileDetailView

from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
    url(r"^$", DashboardView.as_view(dashboard=True), name="dashboard"),
    url(r"^feed", DashboardView.as_view(feed=True), name="db_feed"),

    url(r"^contribution", DashboardView.as_view(contrib=True), name="contrib"),
    url(r"^collaboration", DashboardView.as_view(collaboration=True), name="collaboration"),
    url(r"^drafts", DashboardView.as_view(drafts=True), name="drafts"),
    url(r"^all_contributions", DashboardView.as_view(all_contrib=True), name="all_contrib"),

    url(r"^shopping_notes", DashboardView.as_view(shop_notes=True), name="shop_notes"),
    url(r"^purchase_history", DashboardView.as_view(purch_histo=True), name="purch_histo"),

    url(r"^demo_profile", DashboardView.as_view(demo_profile=True), name="demo_profile"),
)