from django.conf.urls.defaults import patterns, include, url

from profiles.views import MyProfileDetailView


urlpatterns = patterns('',
    url(r"^profile/(?P<username>[\w\._-]+)/$",
            MyProfileDetailView.as_view(), name="profile_detail"),
    url(r"^(?P<profile_slug>[\w\._-]+)/profile/(?P<profile_pk>\d+)/$",
            MyProfileDetailView.as_view(), name="profile_detail"),
)
