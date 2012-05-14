# Create your views here.
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic import View, FormView, ListView, CreateView, DetailView, UpdateView
from items.models import *
from django.db.models.loading import get_model
from django.core.urlresolvers import resolve

app_name = 'items'

class ContentView(View):
    def dispatch(self, request, *args, **kwargs):
        self.model = get_model(app_name, kwargs['model_name'])
        return super(ContentView, self).dispatch(request, *args, **kwargs)

class ContentCreateView(ContentView, CreateView): pass
class ContentUpdateView(ContentView, UpdateView): pass
class ContentDetailView(ContentView, DetailView): pass
