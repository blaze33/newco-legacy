from account.utils import user_display


def profile(request):
    result = {}
    if request.user.is_authenticated():
        profile = request.user.get_profile()
        result.update({"PROFILE": profile, "USERNAME": user_display(profile)})
    return result
