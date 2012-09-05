from django.contrib.auth.models import User
from account.views import LoginView, SignupView
from account.forms import LoginEmailForm

from custaccount.forms import SignupForm


class LoginView(LoginView):

    form_class = LoginEmailForm


class SignupView(SignupView):

    form_class = SignupForm

    def generate_username(self, form):
        # Dummy implementation, username is later set to user auto_id field
        username = unicode(User.objects.count() + 1) + "_makemefeelunique"
        return username

    def create_account(self, form):
        self.created_user.username = unicode(self.created_user.id)
        self.created_user.save()
        self.update_profile(form)
        return super(SignupView, self).create_account(form)

    def update_profile(self, form):
        profile = self.created_user.get_profile()
        profile.name = form.cleaned_data["profile_name"]
        profile.save()
