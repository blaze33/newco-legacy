from django.conf.urls import patterns, include, url

from profiles.views import ProfileRedirectView, ProfileDetailView
from idios.views import ProfileListView, ProfileUpdateView, ProfileCreateView


urlpatterns = patterns('',
    url(r"^$", ProfileListView.as_view(), name="profile_list"),
    url(r"^all/$", ProfileListView.as_view(all_profiles=True),
                                            name="profile_list_all"),

    url(r"^profile/(?P<username>[\w\._-]+)/$",
            ProfileRedirectView.as_view(), name="profile_detail"),
    url(r"^profile/(?P<username>[\w\._-]+)/(?P<slug>[\w\._-]+)/$",
            ProfileDetailView.as_view(), name="profile_detail_full"),

    url(r"^edit/$", ProfileUpdateView.as_view(), name="profile_edit"),
    url(r"^create/$", ProfileCreateView.as_view(), name="profile_create"),
    url(r"^", include("idios.urls")),
)
