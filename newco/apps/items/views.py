# Create your views here.
from django.http import HttpResponseRedirect
from django.views.generic import View, ListView, CreateView, DetailView
from django.views.generic import UpdateView, DeleteView
from django.views.generic.base import RedirectView
from django.views.generic.edit import ProcessFormView, FormMixin
from items.models import Item, CannotManage
from items.forms import QuestionForm, AnswerForm, ItemForm
from django.db.models.loading import get_model
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from taggit.models import Tag
from voting.models import Vote
from django.db.models import Sum
from generic_aggregation import generic_annotate

from pinax.apps.account.utils import user_display
from django.utils.translation import ugettext

from affiliation.models import AffiliationItem

app_name = 'items'


class ContentView(View):

    def dispatch(self, request, *args, **kwargs):
        if 'model_name' in kwargs:
            self.model = get_model(app_name, kwargs['model_name'])
            form_class_name = self.model._meta.object_name + 'Form'
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
            context['affs'] = AffiliationItem.objects.filter(item=self.object)

            questions = self.object.question_set.order_by('-pub_date')
            q_ordered = list(generic_annotate(questions,
                                Vote, Sum('votes__vote'),
                                alias='score').order_by('-score', '-pub_date'))
            for q in questions:
                if q not in q_ordered:
                    q_ordered.append(q)

            context['questions'] = q_ordered
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
                messages.add_message(request, messages.SUCCESS,
                    ugettext(u"Thanks %(user)s, question successfully \
                             submitted") % {"user": user_display(form.user)
                    }
                )
                return self.form_valid(form, request, **kwargs)
            else:
                return self.form_invalid(form)
        else:
            return self.form_invalid(form)


class ContentListView(ContentView, ListView, RedirectView):

    def get_queryset(self):
        if 'tag_slug' in self.kwargs:
            tag = Tag.objects.get(slug=self.kwargs['tag_slug'])
            return Item.objects.filter(tags=tag)
        else:
            return super(ContentListView, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super(ContentListView, self).get_context_data(**kwargs)
        if 'tag_slug' in self.kwargs:
            context['tag'] = Tag.objects.get(slug=self.kwargs['tag_slug'])
        return context

    def post(self, request, *args, **kwargs):
        if 'item_name' in request.POST:
            item_name = request.POST['item_name']
            item = Item.objects.filter(name=item_name)[0]
            return HttpResponseRedirect(item.get_absolute_url())
        else:
            return super(ContentListView, self).post(request, *args, **kwargs)


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
