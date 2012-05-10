from django.shortcuts import get_object_or_404

from django.views.generic import ListView, DetailView

from pp.models import DProduct
from configurableproduct.models import ProductType


class ProductByPTListView(ListView):

    context_object_name = "product_list"
    template_name = "pp/products_by_producttype.html"

    def get_queryset(self):
        self.producttype = get_object_or_404(ProductType,
                                             name__iexact=self.args[0])
        return DProduct.objects.filter(type=self.producttype)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ProductByPTListView, self).get_context_data(**kwargs)
        # Add in the publisher
        context['producttype'] = self.producttype
        return context


class ProductDetailView(DetailView):

    context_object_name = "product"
    queryset = DProduct.objects.all()

    def get_object(self):
        # Call the superclass
        object = super(ProductDetailView, self).get_object()
        # Return the object
        return object
