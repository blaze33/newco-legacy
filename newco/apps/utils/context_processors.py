from django.conf import settings

from django.contrib.sites.models import Site


def site_settings(request):
    site = Site.objects.get_current()
    return {
        "SITE_NAME": site.name,
        "SITE_DOMAIN": site.domain
    }


def settings_mp(request):
    return {
        "MIXPANEL_KEY_ID": settings.MIXPANEL_KEY_ID,
    }
