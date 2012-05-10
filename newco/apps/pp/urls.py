from django.conf.urls.defaults import patterns, url, include
from django.views.generic import ListView
from configurableproduct.models import ProductType

from pp.views import ProductByPTListView, ProductDetailView


urlpatterns = patterns('',
    url(r'^products/$', ListView.as_view(model=ProductType,
                                context_object_name="producttype_list")),
)

urlpatterns += patterns('',
    url(r'^products/(\w+)/$', ProductByPTListView.as_view(),
            name='producttype_detail'),
    url(r'^products/product/(?P<pk>\d+)/$', ProductDetailView.as_view(),
            name='product_detail'),
)
