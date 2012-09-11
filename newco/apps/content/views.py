# Create your views here.
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic import View, FormView, ListView, CreateView, DetailView, UpdateView, DeleteView
from django.views.generic.edit import ProcessFormView, FormMixin
from content.models import Item, Relation
from django.db.models.loading import get_model
from django.core.urlresolvers import resolve, reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required
from django.forms.models import formset_factory
from content.forms import ItemForm, RelationForm

app_name = 'content'


class ContentView(View):

    def dispatch(self, request, *args, **kwargs):
        if self.model:
            self.model_name = self.model._meta.module_name
        if 'model_name' in kwargs:
            self.model_name = kwargs['model_name']
            self.model = get_model(app_name, self.model_name)
            form_class_name = kwargs['model_name'].title()+'Form'
            # form_class_name = 'ContentForm'
            if form_class_name in globals():
                self.form_class = globals()[form_class_name]
            print self.form_class
        return super(ContentView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """ Redirect to the correct slug if needed.
        """
        try:
            self.object = self.get_object()
            slug = self.object.get('slug')
            if slug and kwargs['slug'] != slug:
                url = self.object.get_absolute_url()
                return HttpResponsePermanentRedirect(url)
        except:
            pass #no get_object method, we're not accessing a single object.
        return super(ContentView, self).get(request, *args, **kwargs)

    def get_template_names(self):
        names = []
        if self.template_name_suffix:
            names.append("%s/%s%s.html" % (app_name, app_name,self.template_name_suffix))
            return names
        return super(ContentView, self).get_template_names()

    def get_context_data(self, **kwargs):
        context = super(ContentView, self).get_context_data(**kwargs)
        context['model'] = self.model_name.lower()
        return context

class ContentFormMixin(object):
    """ ContentFormMixin
    Pass request to the form constructor.
    Especially useful to get request.user.
    """

    object = None

    def get(self, request, *args, **kwargs):
        if self.form_class:
            form = self.form_class(**{'request':request})
        else:
            form_class = self.get_form_class()
            form = self.get_form(form_class)
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        if self.form_class:
            form_kwargs = self.get_form_kwargs()
            form_kwargs.update({'request':request})
            form = self.form_class(**form_kwargs)
        else:
            form_class = self.get_form_class()
            form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

class ContentCreateView(ContentView, ContentFormMixin, CreateView): pass
class ContentUpdateView(ContentView, UpdateView): pass

class ContentDetailView(ContentView, DetailView, ProcessFormView, FormMixin):

    def get_context_data(self, **kwargs):
        context = super(ContentDetailView, self).get_context_data(**kwargs)
        context['item'] = self.get_object()
        context['relation_form'] = RelationForm(request=self.request)
        return context

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form, request, **kwargs):
        if form.cleaned_data:
            self.object = form.save(**kwargs)
            form.save_m2m()
        return HttpResponseRedirect(self.get_object().get_absolute_url())

    def post(self, request, *args, **kwargs):
        form = self.form_class(self.request.POST, request=request)
        if form.is_valid():
            return self.form_valid(form, request, **kwargs)
        else:
            return self.form_invalid(form)

class ContentListView(ContentView, ListView): pass

class ContentDeleteView(ContentView, DeleteView):

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not request.user.has_perm("can_manage", self.object):
            raise PermissionDenied
        success_url = self.get_success_url(request)
        self.object.delete()
        return HttpResponseRedirect(success_url)

    def get_success_url(self, request):
        if "success_url" in request.GET:
            success_url = request.GET.get("success_url")
        elif self.model == Relation:
            success_url = self.object.from_item.get_absolute_url()
        else:
            success_url = reverse("content_index")

        if success_url != self.object.get_absolute_url() and success_url is not None:
            return success_url
        raise ImproperlyConfigured