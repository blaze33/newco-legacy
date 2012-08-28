from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic.simple import redirect_to

import autocomplete_light
autocomplete_light.autodiscover()

from django.contrib import admin
admin.autodiscover()

from profiles.views import ProfileDetailView
from content.api import ItemResource, RelationResource

item_resource = ItemResource()
relation_resource = RelationResource()

handler500 = "pinax.views.server_error"


urlpatterns = patterns("",
    url(r"^$", ProfileDetailView.as_view(is_profile_page=False), name="home"),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^admin_tools/", include("admin_tools.urls")),
    url(r"^about/", include("about.urls")),
    url(r"^account/", include("custaccount.urls")),
    url(r"^announcements/", include("announcements.urls")),
    url(r"^content/", include("items.urls")),
    url(r"^content2/", include("content.urls")),
    url(r'^api/', include(item_resource.urls)),
    url(r'^api/', include(relation_resource.urls)),
    url(r"^profiles/", include("profiles.urls")),
    url(r"^taggit_autosuggest/", include("taggit_autosuggest.urls")),
    url(r"^autocomplete/", include("autocomplete_light.urls")),
    url(r"^utils/", include("utils.urls")),
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
