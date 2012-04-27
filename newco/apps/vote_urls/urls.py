from django.conf.urls.defaults import patterns, include, url
from django.db import models
from reviews.models import Review


object_dict = {
    'model': Review,
    'template_object_name': 'object',
    'slug_field': 'slug',
    'allow_xmlhttprequest': False,
}

urlpatterns = patterns('voting.views',
    url(r'^votes/(?P<object_id>\d+)/(?P<direction>up|down|clear)vote/?$', 'vote_on_object', object_dict, name='object_voting'),
)