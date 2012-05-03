from django.conf.urls.defaults import patterns, url, include
from django.views.generic import ListView
from pp.models import DProduct


urlpatterns = patterns('pp.views',
    url(r'^products/$', 'index', name='product_index'),
    url(r'^products/product/(?P<product_id>\d+)/$', 'detail', name='product_detail'),
)

urlpatterns += patterns('',
    url(r'^products2/$', ListView.as_view(
        model=DProduct,
        context_object_name="product_list",
    )),
)
