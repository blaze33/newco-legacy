# Create your views here.
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic import FormView, ListView, CreateView, DetailView, UpdateView
from items.models import *
from django.db.models.loading import get_model

class ItemView(FormView):
    model = Item

class ContentCreateView(CreateView):
    def get(self, request, *args, **kwargs):
        self.model = get_model("items", kwargs['model_name'])
        return super(ContentCreateView, self).get(request, *args, **kwargs)

class ItemUpdateView(ItemView, UpdateView):
    def get_object(self, queryset=None):
        obj = Item.objects.get(pk=self.kwargs['id'])
        return obj

class ItemDetailView(DetailView):
    model=Item,
    context_object_name="item"
    
    def get_queryset(self):
        return Item.objects.filter(pk=self.kwargs['item_id'])
