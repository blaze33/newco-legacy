# Create your views here.
from django.http import HttpResponseRedirect
from django.views.generic import View, ListView, CreateView, DetailView
from django.views.generic import UpdateView, DeleteView
from django.views.generic.edit import ProcessFormView, FormMixin
from items.models import Item, CannotManage
from items.forms import QuestionForm, AnswerForm, ItemForm
from django.db.models.loading import get_model
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required

from profiles.models import Profile

app_name = 'items'


class ContentView(View):

    def dispatch(self, request, *args, **kwargs):
        if 'model_name' in kwargs:
            self.model = get_model(app_name, kwargs['model_name'])
            form_class_name = kwargs['model_name'].title() + 'Form'
            if form_class_name in globals():
                self.form_class = globals()[form_class_name]
        return super(ContentView, self).dispatch(request, *args, **kwargs)


class ContentFormMixin(object):

    object = None

    def get(self, request, *args, **kwargs):
        if self.form_class:
            form = self.form_class(**{'request': request})
        else:
            form_class = self.get_form_class()
            form = self.get_form(form_class)
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        if self.form_class:
            form_kwargs = self.get_form_kwargs()
            form_kwargs.update({'request': request})
            form = self.form_class(**form_kwargs)
        else:
            form_class = self.get_form_class()
            form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class ContentCreateView(ContentView, ContentFormMixin, CreateView):

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ContentCreateView, self).dispatch(request,
                                                       *args,
                                                       **kwargs)


class ContentUpdateView(ContentView, UpdateView):

#    @method_decorator(permission_required(app_name))
    def dispatch(self, request, *args, **kwargs):
        return super(ContentUpdateView, self).dispatch(request,
                                                       *args,
                                                       **kwargs)


class ContentDetailView(ContentView, DetailView, ProcessFormView, FormMixin):

    def get_context_data(self, **kwargs):
        context = super(ContentDetailView, self).get_context_data(**kwargs)
        self.object = self.get_object()
        if self.model == Item:
            if self.request.POST:
                f = QuestionForm(self.request.POST, request=self.request)
            else:
                f = QuestionForm(request=self.request)
            context['form'] = f
            context['item'] = self.object
            context['list_users'] = self.object.compute_tags(Profile.objects.all())
        return context

    def form_invalid(self, form):
        self.object = self.get_object()
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form, request, **kwargs):
        if form.cleaned_data:
            self.object = form.save(**kwargs)
            form.save_m2m()
        return HttpResponseRedirect(self.get_object().get_absolute_url())

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        if 'question_ask' in request.POST:
            form = QuestionForm(self.request.POST, request=request)
            if form.is_valid():
                return self.form_valid(form, request, **kwargs)
            else:
                return self.form_invalid(form)
        else:
            return self.form_invalid(form)


class ContentListView(ContentView, ListView):
    pass


class ContentDeleteView(ContentView, DeleteView):

    def delete(self, request, *args, **kwargs):
        if 'success_url' in request.REQUEST:
            self.success_url = request.REQUEST['success_url']
        self.object = self.get_object()
        try:
            if not self.object.user_can_manage_me(request.user):
                raise CannotManage
        except CannotManage:
            # need to redirect to 403 - delete forbidden
            return HttpResponseRedirect(self.get_success_url())
        except AttributeError:
            pass
        self.object.delete()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        if self.model.__name__ == 'Item':
            return reverse("item_index")
        if self.success_url:
            return self.success_url
