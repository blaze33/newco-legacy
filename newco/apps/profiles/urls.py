from django.conf.urls import patterns, include, url
from idios.views import ProfileUpdateView

from profiles.views import ProfileDetailView, ProfileListView


urlpatterns = patterns('',
    url(r"^profile/(?P<pk>\d+)/(?P<slug>[\w\._-]*)",
            ProfileDetailView.as_view(), name="profile_detail"),
   #  url(r"^profile2/(?P<pk>\d+)/(?P<slug>[\w\._-]*)/$",
   #          ProfileDetailView.as_view(demo_dashboard=True)), ## For demo only line to be deleted ##
   #  url(r"^profile2/(?P<pk>\d+)/(?P<slug>[\w\._-]*)/feed",
   #          ProfileDetailView.as_view(demo_feed=True)), ## For demo only line to be deleted ##
   #  url(r"^profile2/(?P<pk>\d+)/(?P<slug>[\w\._-]*)/dashboard_contrib",
   #          ProfileDetailView.as_view(demo_dashboard_contrib=True)), ## For demo only line to be deleted ##
   #  url(r"^profile2/(?P<pk>\d+)/(?P<slug>[\w\._-]*)/collaboration",
   #          ProfileDetailView.as_view(demo_collaboration=True)), ## For demo only line to be deleted ##
   #  url(r"^profile2/(?P<pk>\d+)/(?P<slug>[\w\._-]*)/draft",
   #          ProfileDetailView.as_view(demo_draft=True)), ## For demo only line to be deleted ##
   #  url(r"^profile2/(?P<pk>\d+)/(?P<slug>[\w\._-]*)/allcontrib",
   #          ProfileDetailView.as_view(demo_allcontrib=True)), ## For demo only line to be deleted ##
   # url(r"^profile2/(?P<pk>\d+)/(?P<slug>[\w\._-]*)/shopping_notes",
   #          ProfileDetailView.as_view(demo_shopping_notes=True)), ## For demo only line to be deleted ##
   # url(r"^profile2/(?P<pk>\d+)/(?P<slug>[\w\._-]*)/purchase_history",
   #          ProfileDetailView.as_view(demo_purchase_history=True)), ## For demo only line to be deleted ##

    
    url(r"^edit/$", ProfileUpdateView.as_view(), name="profile_edit"),
    url(r"^$", ProfileListView.as_view(), name="profile_list"),
    url(r"^all/$", ProfileListView.as_view(all_profiles=True), name="profile_list_all"),
    url(r"^", include("idios.urls")),
)
