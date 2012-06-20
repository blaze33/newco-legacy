from django.conf.urls import patterns, include, url

from custaccount.views import LoginView, SignupView


urlpatterns = patterns("",
    url(r"^signup/$", SignupView.as_view(), name="account_signup"),
    url(r"^login/$", LoginView.as_view(), name="account_login"),
    url(r"^", include("account.urls")),
)
