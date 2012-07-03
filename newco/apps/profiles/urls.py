from django.conf.urls import patterns, include, url
from idios.views import ProfileUpdateView

from profiles.views import ProfileDetailView


urlpatterns = patterns('',
    url(r"^profile/(?P<pk>\d+)/(?P<slug>[\w\._-]*)",
            ProfileDetailView.as_view(), name="profile_detail"),
    url(r"^edit/$", ProfileUpdateView.as_view(), name="profile_edit"),
    url(r"^", include("idios.urls")),
)
