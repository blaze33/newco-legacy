from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic.simple import direct_to_template
from django.views.generic.simple import redirect_to

from django.contrib import admin
admin.autodiscover()


handler500 = "pinax.views.server_error"


urlpatterns = patterns("",
    url(r"^$", direct_to_template, {
        "template": "homepage.html",
    }, name="home"),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^about/", include("about.urls")),
    url(r"^account/", include("account.urls")),
    url(r"^announcements/", include("announcements.urls")),
    url(r"^votes/", include("votes.urls")),
    url(r"^content/", include("items.urls")),
    url(r"^profiles/", include("profiles.urls")),
    url(r"^profiles/", include("idios.urls")),

    # commented for django 1.4
    # url(r"^notices/", include("notification.urls")),
)

urlpatterns += patterns("",
    url(r"^Friends/(?P<path>.*)$", redirect_to, {
            'url': 'http://static.newco-project.fr/Friends/%(path)s',
            'permanent': True
        }
    ),
    url(r"^static/(?P<path>.*)$", redirect_to, {
            'url': 'http://static.newco-project.fr/static/%(path)s',
            'permanent': True
        }
    ),
)

if settings.SERVE_MEDIA:
    urlpatterns += patterns("",
        url(r"", include("staticfiles.urls")),
    )
