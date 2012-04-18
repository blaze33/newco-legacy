from django.conf.urls.defaults import patterns, include, url


urlpatterns = patterns('',
    url(r'^products/$', 'pp.views.index'),
    url(r'^products/(?P<product_id>\d+)/$', 'pp.views.detail'),
)