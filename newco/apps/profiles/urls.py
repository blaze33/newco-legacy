from django.conf.urls import patterns, include, url

from profiles.views import ProfileRedirectView, ProfileDetailView


urlpatterns = patterns('',
    url(r"^profile/(?P<username>[\w\._-]+)/$",
            ProfileRedirectView.as_view(), name="profile_detail"),
    url(r"^profile/(?P<username>[\w\._-]+)/(?P<slug>[\w\._-]+)/$",
            ProfileDetailView.as_view(), name="profile_detail_full"),
    url(r"^(?P<profile_slug>[\w\._-]+)/profile/(?P<profile_pk>\d+)/$",
            ProfileDetailView.as_view(), name="profile_detail_full"),
    url(r"^", include("idios.urls")),
)
