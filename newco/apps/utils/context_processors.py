import json

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder

from django.contrib.sites.models import Site

from account.utils import user_display


def site_settings(request):
    site = Site.objects.get_current()
    return {
        "SITE_NAME": site.name,
        "SITE_DOMAIN": site.domain
    }


def settings_mp(request):
    output = {"MIXPANEL_KEY_ID": settings.MIXPANEL_KEY_ID}
    user = request.user
    if user.is_authenticated():
        profile = user.get_profile()
        data = {"userId": user.id, "email": user.email, "bio": profile.about,
                "created": user.date_joined, "name": user_display(profile),
                "reputation": user.reputation.reputation_incremented}
    else:
        data = {"userId": 0}
    output = {"MIXPANEL_KEY_ID": settings.MIXPANEL_KEY_ID,
              "user_json": json.dumps(data, cls=DjangoJSONEncoder)}
    return output
