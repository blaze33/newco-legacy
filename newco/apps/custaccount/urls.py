from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required

from custaccount.views import LoginView, SignupView

admin.autodiscover()
admin.site.login = login_required(admin.site.login)


urlpatterns = patterns("",
    url(r"^signup/$", SignupView.as_view(), name="account_signup"),
    url(r"^login/$", LoginView.as_view(), name="account_login"),
    url(r"^", include("account.urls")),
)
