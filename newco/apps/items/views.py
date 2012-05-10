# Create your views here.
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic import ListView, CreateView, DetailView
from items.models import Item

def index(request):
    return HttpResponse("Hello, world. You're at the poll index.")
    
def detail(request, item_id):
    i = get_object_or_404(Item, pk=item_id)
    return HttpResponse("You're looking at item %s." % item_id,
    )

class ItemCreateView(CreateView):
    # form_class = AuthorForm
    model = Item

    # template_name = 'author_new.html'
    #success_url = 'success'

class ItemDetailView(DetailView):
    model=Item,
    context_object_name="item"
    
    def get_queryset(self):
        item = get_object_or_404(Item.objects, pk=self.kwargs['item_id'])
        return Item.objects.filter(pk=self.kwargs['item_id'])
