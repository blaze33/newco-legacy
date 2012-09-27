from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic.simple import redirect_to

import autocomplete_light
autocomplete_light.autodiscover()

from django.contrib import admin
admin.autodiscover()

from content.api import ItemResource, RelationResource
from sitemaps import all_sitemaps as sitemaps
from tastypie.api import Api
from utils.views.autocomplete import redis_to_json
from views import HomepageView


v1_api = Api(api_name='v1')
v1_api.register(ItemResource())
v1_api.register(RelationResource())

handler500 = "pinax.views.server_error"


urlpatterns = patterns("",
    url(r"^$", HomepageView.as_view(), name="home"),
    url(r"^(?P<cat>last|newsfeed)$", HomepageView.as_view(), name="home"),
    url(r"^content$", HomepageView.as_view(), name="item_index"),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^admin_tools/", include("admin_tools.urls")),
    url(r"^about/", include("about.urls")),
    url(r"^account/", include("custaccount.urls")),
    url(r"^announcements/", include("announcements.urls")),
    url(r"^content/", include("items.urls")),
    url(r"^dashboard/", include("dashboard.urls")),
    url(r"^content2/", include("content.urls")),
    url(r'^api/', include(v1_api.urls)),
    url(r"^profiles/", include("profiles.urls")),
    url(r"^taggit_autosuggest/", include("taggit_autosuggest.urls")),
    url(r"^autocomplete/", include("autocomplete_light.urls")),
    url(r"^utils/", include("utils.urls")),
    url(r"^redis/search", redis_to_json, name="redis"),
    url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.index', {'sitemaps': sitemaps}),
    url(r'^sitemap-(?P<section>.+)\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),

)

if settings.DEBUG:
    urlpatterns += patterns("",
        url(r"^rosetta/", include("rosetta.urls")),
    )

urlpatterns += patterns("",
    url(r"^(.)riends/(?P<path>.*)$", redirect_to, {
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
