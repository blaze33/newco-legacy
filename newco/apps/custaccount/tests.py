from django.db import transaction
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test.client import Client, RequestFactory
from django.utils import unittest
from django.utils.importlib import import_module

from django.contrib.auth.models import AnonymousUser, User

from account.forms import LoginEmailForm
from account.utils import user_display

from .forms import SignupForm
from .views import SignupView, LoginView


class SignupEnabledView(SignupView):

    def is_open(self):
        return True


class SignupDisabledView(SignupView):

    def is_open(self):
        return False


class SignupRedirectView(SignupView):
    pass


class LoginDisabledView(LoginView):

    def disabled(self):
        return True


class LoginRedirectView(LoginView):

    def login_user(self, form):
        return True


class SignupViewTestCase(unittest.TestCase):

    def setUp(self):
        self.factory = RequestFactory()

        settings.SESSION_ENGINE = 'django.contrib.sessions.backends.file'
        engine = import_module(settings.SESSION_ENGINE)
        store = engine.SessionStore()
        store.save()
        self.session = store

        self.client = Client()
        self.client.cookies[settings.SESSION_COOKIE_NAME] = store.session_key

    def test_get(self):
        request = self.factory.get(reverse("account_signup"))
        request.user = AnonymousUser()
        response = SignupEnabledView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_get_disabled(self):
        request = self.factory.get(reverse("account_signup"))
        request.user = AnonymousUser()
        response = SignupDisabledView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, "account/signup_closed.html")

    def test_post_disabled(self):
        request = self.factory.post(reverse("account_signup"))
        request.user = AnonymousUser()
        response = SignupDisabledView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, "account/signup_closed.html")

    def test_post_successful(self):
        post = {"email": "info@example.com", "password": "pwd",
                "password_confirm": "pwd", "profile_name": "bob"}
        request = self.factory.post(reverse("account_signup"), post)
        request.user = AnonymousUser()

        # workaround bug in django 1.4
        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, 'session', self.session)
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = SignupEnabledView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(email="info@example.com")
        self.assertEqual(user_display(user), "bob")
        user.delete()

    @transaction.commit_manually
    def test_custom_redirect_field(self):
        request = self.factory.request()
        request.user = AnonymousUser()

        # workaround bug in django 1.4
        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, 'session', self.session)
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        sid = transaction.savepoint()

        request.GET = {"next_page": "/profiles/"}
        form = SignupForm({"email": "someone@example.com", "password": "pass",
                           "password_confirm": "pass", "profile_name": "bob"})
        view = SignupRedirectView(request=request,
                                  redirect_field_name="next_page")
        self.assertTrue(form.is_valid())
        self.assertEqual("/profiles/", view.form_valid(form)["Location"])

        transaction.savepoint_rollback(sid)
        transaction.commit()


class LoginViewTestCase(unittest.TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_get(self):
        request = self.factory.get(reverse("account_login"))
        request.user = AnonymousUser()
        response = LoginView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ["account/login.html"])

    def test_custom_redirect_field(self):
        request = self.factory.request()
        request.GET = {"next_page": "/profiles/"}
        form = LoginEmailForm({"email": "someone@example.com",
                               "password": "password"})
        view = LoginRedirectView(request=request,
                                 redirect_field_name="next_page")
        self.assertEqual("/profiles/", view.form_valid(form)["Location"])
