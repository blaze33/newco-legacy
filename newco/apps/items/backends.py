

class ItemBackend(object):

    def authenticate(self, username=None, password=None):
        return None

    def get_user(self, user_id):
        return None

    def has_perm(self, user_obj, perm, obj=None):
        if perm == "can_manage":
            if user_obj.is_active:
                try:
                    if user_obj == obj.author:
                        return user_obj == obj.author or user_obj.is_superuser
                except AttributeError:
                    pass
                return user_obj.is_superuser

        return False
