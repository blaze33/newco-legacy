from django.core.exceptions import PermissionDenied

from django.contrib.auth.decorators import user_passes_test


def staff_member_required(login_url=None, raise_exception=False):
    """
    Decorator for views that checks whether a user is staff,
    redirecting to the log-in page if neccesary.
    If the raise_exception parameter is given the PermissionDenied exception
    is raised.
    """
    def check_staff(user):
        if user.is_staff:
            return True
        # In case the 403 handler should be called raise the exception
        if user.is_authenticated() and raise_exception:
            raise PermissionDenied()
        # As the last resort, show the login form
        return False
    return user_passes_test(check_staff, login_url=login_url)
