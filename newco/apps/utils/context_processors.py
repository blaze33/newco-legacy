import json

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder

from account.utils import user_display


def mixpanel(request):
    user = request.user
    if user.is_authenticated():
        profile = user.get_profile()
        data = {"userId": user.id, "email": user.email, "bio": profile.about,
                "created": user.date_joined, "name": user_display(profile),
                "reputation": user.reputation.reputation_incremented}
    else:
        data = {"userId": 0}
    user = json.dumps(data, cls=DjangoJSONEncoder).replace(
        "\\r", "\\\\r").replace("\\n", "\\\\n")
    output = {"MIXPANEL_KEY_ID": settings.MIXPANEL_KEY_ID, "user_json": user}
    return output
