from django.conf.urls import patterns, include, url
from utils.views.autocomplete import autocomplete

urlpatterns = patterns('',
    url(r"^autocomplete/$", autocomplete, name="autocomplete"),
)
