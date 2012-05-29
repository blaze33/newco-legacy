# Create your views here.
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic import View, FormView, ListView, CreateView, DetailView, UpdateView, DeleteView
from django.views.generic.edit import ProcessFormView, FormMixin
from items.models import *
from django.db.models.loading import get_model
from django.core.urlresolvers import resolve, reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required
from django.forms.models import formset_factory

app_name = 'items'

class ContentView(View):
    def dispatch(self, request, *args, **kwargs):
        if 'model_name' in kwargs:
            self.model = get_model(app_name, kwargs['model_name'])
            form_class_name = kwargs['model_name'].title()+'Form'
            if form_class_name in globals():
                self.form_class = globals()[form_class_name]
        return super(ContentView, self).dispatch(request, *args, **kwargs)

class ContentFormMixin(object):

    object = None

    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.form_class(**{'request':request})
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form_kwargs = self.get_form_kwargs()
        form_kwargs.update({'request':request})
        form = self.form_class(**form_kwargs)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

class ContentCreateView(ContentView, ContentFormMixin, CreateView): pass
class ContentUpdateView(ContentView, UpdateView): pass

class ContentDetailView(ContentView, DetailView, ProcessFormView, FormMixin):

    def get_context_data(self, **kwargs):
        context = super(ContentDetailView, self).get_context_data(**kwargs)
        self.object = self.get_object()
        if self.model == Item:
            QuestionFormSet = formset_factory(QuestionForm)
            if self.request.POST:
                fs = QuestionFormSet(self.request.POST, prefix='questions')
            else:
                fs = QuestionFormSet(prefix='questions')
            context['formset'] = fs
            context['item'] = self.object
        return context

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, formset, request, **kwargs):
        for form in formset:
            if form.cleaned_data:
                self.object = form.save(request, **kwargs)
                form.save_m2m()     
        return HttpResponseRedirect(self.get_object().get_absolute_url())

    def post(self, request, *args, **kwargs):
        if 'question_ask' in request.POST:
            self.formset_class = formset_factory(QuestionForm)
            formset = self.formset_class(data=self.request.POST,
                                         prefix='questions')
            if formset.is_valid():
                return self.form_valid(formset, request, **kwargs)
        else:
            return self.form_invalid(form)
    
class ContentListView(ContentView, ListView): pass

class ContentDeleteView(ContentView, DeleteView):

    @method_decorator(permission_required('is_superuser'))
    def delete(self, request, *args, **kwargs):
        if 'success_url' in request.REQUEST:
            self.success_url = request.REQUEST['success_url']
        return super(ContentDeleteView, self).delete(request, *args, **kwargs)

    def get_success_url(self):
        if self.success_url:
            return self.success_url
        model_name = self.model.__name__
        if model_name == "Question":
            return self.object.item.get_absolute_url()
        else:
            return reverse("item_index")
