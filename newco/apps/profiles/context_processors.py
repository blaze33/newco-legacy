from account.utils import user_display


def profile(request):
    if request.user.is_authenticated():
        profile = request.user.get_profile()
        return {
            "PROFILE": profile,
            "USERNAME": user_display(profile)
        }
