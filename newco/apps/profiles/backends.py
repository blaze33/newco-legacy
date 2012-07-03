from account.auth_backends import EmailAuthenticationBackend


class ProfileBackend(EmailAuthenticationBackend):

    def has_perm(self, user_obj, perm, obj=None):
        if perm == "can_view":
            return True
        else:
            return False
