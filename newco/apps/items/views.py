# Create your views here.
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic import ListView, CreateView, DetailView
from items.models import Item

class ItemCreateView(CreateView):
    # form_class = AuthorForm
    model = Item

class ItemDetailView(DetailView):
    model=Item,
    context_object_name="item"
    
    def get_queryset(self):
        return Item.objects.filter(pk=self.kwargs['item_id'])
