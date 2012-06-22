from django.contrib.auth.models import User, Permission


class ProfileBackend(object):

    def has_perm(self, user_obj, perm, obj=None):
        if perm == "can_view":
            return True
        else:
            return False
