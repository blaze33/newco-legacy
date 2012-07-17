

class ProfileBackend(object):

    def authenticate(self, username=None, password=None):
        return None

    def get_user(self, user_id):
        return None

    def has_perm(self, user_obj, perm, obj=None):
        if perm == "can_view":
            return True
        else:
            return False
