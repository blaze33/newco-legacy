from django.conf import settings
from django.forms import Field
from django.template import Context, loader, RequestContext
from django.http import HttpResponse, Http404, HttpRequest
from django.shortcuts import render_to_response, get_object_or_404

from django.contrib.comments import CommentForm

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

    if request.user.is_authenticated():
        # Hard coding of the user profile url into comment url
        profile_url = request.user.get_profile().get_absolute_url()
        form = CommentForm(p, initial={'url': request.build_absolute_uri(profile_url)})
    else:
        form = CommentForm(p)
    
    # Hide unwanted fields
    for attr in {'name', 'url', 'email', 'honeypot'}:
        form.fields[attr].widget = Field.hidden_widget()

    return render_to_response('pp/detail.html',
                              {'product': p, 'form' : form},
                              context_instance=RequestContext(request))
