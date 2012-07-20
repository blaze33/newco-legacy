from django.contrib.auth.models import User
from account.views import LoginView, SignupView
from account.forms import LoginEmailForm

from custaccount.forms import SignupForm


class LoginView(LoginView):

    form_class = LoginEmailForm


class SignupView(SignupView):

    form_class = SignupForm

    def generate_username(self, form):
        username = unicode(User.objects.count() + 1)
        return username

    def create_account(self, new_user, form):
        self.update_profile(new_user, form)
        return super(SignupView, self).create_account(new_user, form)

    def update_profile(self, user, form):
        profile = user.get_profile()
        profile.name = form.cleaned_data["profile_name"]
        profile.save()
