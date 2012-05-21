# Create your views here.
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic import View, FormView, ListView, CreateView, DetailView, UpdateView, DeleteView
from items.models import *
from django.db.models.loading import get_model
from django.core.urlresolvers import resolve, reverse

app_name = 'items'

class ContentView(View):
    def dispatch(self, request, *args, **kwargs):
        if 'model_name' in kwargs:
            self.model = get_model(app_name, kwargs['model_name'])
        return super(ContentView, self).dispatch(request, *args, **kwargs)

class ContentCreateView(ContentView, CreateView): pass
class ContentUpdateView(ContentView, UpdateView): pass
class ContentDetailView(ContentView, DetailView): pass
class ContentListView(ContentView, ListView): pass
class ContentDeleteView(ContentView, DeleteView):
    def get_success_url(self):
        model_name = self.model.__name__
        if model_name == "Question":
            return self.object.item.get_absolute_url()
        else:
            return reverse("item_index")
