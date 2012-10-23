from django.conf import settings

def settings_mp(request):
    ctx = {
        "MIXPANEL_KEY_ID": settings.MIXPANEL_KEY_ID,
    }
    return ctx