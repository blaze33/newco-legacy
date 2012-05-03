from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404

from django.views.generic import DetailView

from pp.models import DProduct
from configurableproduct.models import ProductType

def index(request):
    product_list = DProduct.objects.all()
    producttype_list = ProductType.objects.all()
    return render_to_response('pp/index.html',
                              {'product_list': product_list, 'producttype_list': producttype_list},
                              context_instance=RequestContext(request))

def detail(request, product_id):
    p = get_object_or_404(DProduct, pk=product_id)
    return render_to_response('pp/detail.html', {'product': p},
                              context_instance=RequestContext(request))

#class ProductDetailView(DetailView):

#    context_object_name = "dproduct"
#    model = DProduct

#    def get_context_data(self, **kwargs):
#        # Call the base implementation first to get a context
#        context = super(ProductDetailView, self).get_context_data(**kwargs)
#        # Add in a QuerySet of all the books
##        context['book_list'] = Book.objects.all()
#        return context
