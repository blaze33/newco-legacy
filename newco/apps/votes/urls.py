from django.conf.urls.defaults import patterns, include, url


urlpatterns = patterns('votes.views',
    url(r"^(?P<model_name>[-\w]+)/(?P<object_id>\d+)/?$", 'rate_object', name='object_voting'),
)
