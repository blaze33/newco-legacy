from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
    url(r"^(?P<model_name>[-\w]+)/(?P<object_id>\d+)/?$", 'votes.views.rate_object', name='object_voting'),
)
