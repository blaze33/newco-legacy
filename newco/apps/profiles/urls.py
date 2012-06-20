from django.conf.urls import patterns, include, url

from profiles.views import ProfileDetailView


urlpatterns = patterns('',
    url(r"^profile/(?P<username>[\w\._-]+)/$",
            ProfileDetailView.as_view(), name="profile_detail"),
    url(r"^(?P<profile_slug>[\w\._-]+)/profile/(?P<profile_pk>\d+)/$",
            ProfileDetailView.as_view(), name="profile_detail"),
)
