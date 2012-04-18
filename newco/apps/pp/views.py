from django.template import Context, loader, RequestContext
from django.http import HttpResponse, Http404, HttpRequest
from django.shortcuts import render_to_response, get_object_or_404

from django.contrib.comments import CommentForm

from pp.models import DProduct
from configurableproduct.models import ProductType

def index(request):
    product_list = DProduct.objects.all()
    producttype_list = ProductType.objects.all()
    return render_to_response('pp/index.html', {'product_list': product_list, 'producttype_list': producttype_list})

def detail(request, product_id):
    p = get_object_or_404(DProduct, pk=product_id)
    request.user
    if request.user.is_authenticated():
        profile = request.user.get_profile()
        profile_url = profile.get_absolute_url()
        form = CommentForm(p, initial={'url': request.build_absolute_uri(profile_url)})
    else:
        form = CommentForm(p)

    return render_to_response('pp/detail.html', {'product': p, 'form' : form},
                               context_instance=RequestContext(request))