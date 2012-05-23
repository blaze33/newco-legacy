from django.conf.urls.defaults import patterns, include, url
from items.models import Item, Question, Answer


urlpatterns = patterns('voting.views',
    url(r'^question/(?P<object_id>\d+)/(?P<direction>up|down|clear)vote/?$',
            'vote_on_object', {'model': Question}, name='question_voting'),
)
