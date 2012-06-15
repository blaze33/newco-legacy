from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.generic import View, ListView, CreateView, DetailView
from django.views.generic import UpdateView, DeleteView
from django.views.generic.base import RedirectView
from django.views.generic.edit import ProcessFormView, FormMixin
from items.models import Item, CannotManage
from items.forms import QuestionForm, AnswerForm, ItemForm, FeaturePForm, FeatureNForm
from items.forms import ExternalLinkForm
from django.db.models.loading import get_model
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from pinax.apps.account.utils import user_display
from taggit.models import Tag
from voting.models import Vote
from django.db.models import Sum, Count
from generic_aggregation import generic_annotate

from profiles.models import Profile

import json

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

    messages = {
        "object_created": {
            "level": messages.SUCCESS,
            "text": _("Thanks %(user)s, %(object)s successfully created.")
        },
        "creation_failed": {
            "level": messages.ERROR,
            "text": _("Warning %(user)s, %(object)s form is invalid.")
        },
    }

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ContentCreateView, self).dispatch(request,
                                                       *args,
                                                       **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        messages.add_message(
            self.request, self.messages["object_created"]["level"],
            self.messages["object_created"]["text"] % {
                "user": user_display(self.request.user),
                "object": self.object._meta.verbose_name
            }
        )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.add_message(
            self.request, self.messages["creation_failed"]["level"],
            self.messages["creation_failed"]["text"] % {
                "user": user_display(self.request.user),
                "object": form._meta.model._meta.verbose_name
            }
        )
        return super(ContentCreateView, self).form_invalid(form)


class ContentUpdateView(ContentView, UpdateView):

#    @method_decorator(permission_required(app_name))
    def dispatch(self, request, *args, **kwargs):
        return super(ContentUpdateView, self).dispatch(request,
                                                       *args,
                                                       **kwargs)


class ContentDetailView(ContentView, DetailView, ProcessFormView, FormMixin):

    messages = {
        "object_created": {
            "level": messages.SUCCESS,
            "text": _("Thanks %(user)s, %(object)s successfully created.")
        },
        "creation_failed": {
            "level": messages.WARNING,
            "text": _("Warning %(user)s, %(object)s form is invalid.")
        },
    }

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
            
            #ordering questions
            questions = self.object.question_set.all()
            q_ordered = sorted(list(questions),
                key=lambda q: Vote.objects.get_score(q)['score'], reverse=True)

            context['questions'] = q_ordered
            
            #ordering external links
            extlinks = self.object.externallink_set.all()
            e_ordered = sorted(list(extlinks),
                key=lambda e: Vote.objects.get_score(e)['score'], reverse=True)
                                                   
            context['extlinks'] = e_ordered
            
            #ordering features_pos
            features_pos = self.object.featurep_set.all()
            f_ordered_pos = sorted(list(features_pos),
                key=lambda f: Vote.objects.get_score(f)['score'], reverse=True)

            context['features_pos'] = f_ordered_pos
            
            #ordering features_neg
            features_neg = self.object.featuren_set.all()
            f_ordered_neg = sorted(list(features_neg),
                key=lambda f: Vote.objects.get_score(f)['score'], reverse=True)

            context['features_neg'] = f_ordered_neg
            
        return context

    def form_invalid(self, form):
        self.object = self.get_object()
        messages.add_message(self.request,
            self.messages["creation_failed"]["level"],
            self.messages["creation_failed"]["text"] % {
                "user": user_display(self.request.user),
                "object": form._meta.model._meta.verbose_name
            }
        )
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form, request, **kwargs):
        if form.cleaned_data:
            self.object = form.save(**kwargs)
            form.save_m2m()
            messages.add_message(self.request,
                self.messages["object_created"]["level"],
                self.messages["object_created"]["text"] % {
                    "user": user_display(self.request.user),
                    "object": self.object._meta.verbose_name
                }
            )
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


class ContentListView(ContentView, ListView, RedirectView):

    def get_queryset(self):
        if 'tag_slug' in self.kwargs:
            self.tag = Tag.objects.get(slug=self.kwargs['tag_slug'])
            return Item.objects.filter(tags=self.tag)
        else:
            return super(ContentListView, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super(ContentListView, self).get_context_data(**kwargs)
        if hasattr(self, 'tag'):
            context['tag'] = self.tag
        if 'item_list' in context:
            context.update({
                "item_names": json.dumps([item.name \
                                          for item in context['item_list']])
            })
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
