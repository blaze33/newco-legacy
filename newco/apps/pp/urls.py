from django.conf.urls.defaults import patterns, include, url


urlpatterns = patterns('pp.views',
    url(r'^products/$', 'index', name='product_index'),
    url(r'^products/product/(?P<product_id>\d+)/$', 'detail', name='product_detail'),
)