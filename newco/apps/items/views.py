import json

from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.db.models import Q, Sum, Count
from django.db.models.loading import get_model
from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.utils.datastructures import SortedDict
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View, ListView, CreateView, DetailView
from django.views.generic import UpdateView, DeleteView
from django.views.generic.edit import FormMixin

from django.contrib.auth.decorators import login_required
from django.contrib import messages

from account.utils import user_display
from chosen.forms import ChosenSelect
from generic_aggregation import generic_annotate
from taggit.models import Tag
from voting.models import Vote

from content.transition import add_images, get_album
from items.models import Item, Content, Question, Link, Feature
from items.forms import QuestionForm, AnswerForm, ItemForm, QAFormSet
from profiles.models import Profile
from utils.apiservices import search_images
from utils.mailtools import mail_question_author, process_asking_for_help
from utils.follow.views import ProcessFollowView
from utils.tools import load_object, get_sorted_queryset, get_search_results
from utils.vote.views import ProcessVoteView
from utils.multitemplate.views import MultiTemplateMixin

app_name = "items"


class ContentView(View):

    def dispatch(self, request, *args, **kwargs):
        if "model_name" in kwargs:
            self.model = get_model(app_name, kwargs["model_name"])
            if self.model is Link or self.model is Feature:
                raise Http404()
            form_class_name = self.model._meta.object_name + "Form"
            if form_class_name in globals():
                self.form_class = globals()[form_class_name]
        return super(ContentView, self).dispatch(request, *args, **kwargs)


class NextMixin(object):

    def get(self, request, *args, **kwargs):
        if "next" in request.GET:
            kwargs.update({"next": request.GET.get("next")})
        return super(NextMixin, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if "next" in request.POST:
            self.success_url = request.POST.get("next")
        return super(NextMixin, self).post(request, *args, **kwargs)


class ContentFormMixin(NextMixin):

    object = None

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ContentFormMixin, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(ContentFormMixin, self).get_form_kwargs()
        kwargs.update({"request": self.request})
        return kwargs

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if self.model == Item and ("store_search" in request.POST or
                                   "add_links" in request.POST or
                                   "remove_links" in request.POST):
            if "add_links" in request.POST and self.object:
                form.link_aff(self.object)
            if "remove_links" in request.POST and self.object:
                aff_item_ids = request.POST.getlist("linked_aff")
                linked_items = self.object.affiliationitem_set.select_related()
                aff_items_to_delete = linked_items.exclude(id__in=aff_item_ids)
                for aff_item in aff_items_to_delete:
                    aff_item.delete()
            if "store_search" in request.POST:
                form.stores_search()
            return self.render_to_response(self.get_context_data(form=form))
        elif form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class ContentCreateView(ContentView, ContentFormMixin, MultiTemplateMixin,
                        CreateView):

    messages = {
        "created": {
            "level": messages.SUCCESS,
            "text": _("Thanks %(user)s, %(object)s successfully created.")
        },
        "failed": {
            "level": messages.ERROR,
            "text": _("Warning %(user)s, %(object)s form is invalid.")
        },
    }

    def form_valid(self, form):
        self.object = form.save()
        messages.add_message(
            self.request, self.messages["created"]["level"],
            self.messages["created"]["text"] % {
                "user": user_display(self.request.user),
                "object": self.object._meta.verbose_name
            }
        )
        if self.model == Item and "edit" in self.request.POST:
            return HttpResponseRedirect(reverse(
                "item_edit",
                args=[self.object._meta.module_name, self.object.id]
            ))
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.add_message(
            self.request, self.messages["failed"]["level"],
            self.messages["failedfailed"]["text"] % {
                "user": user_display(self.request.user),
                "object": form._meta.model._meta.verbose_name
            }
        )
        return super(ContentCreateView, self).form_invalid(form)

    def post(self, request, *args, **kwargs):
        if self.model is not Question:
            return super(ContentCreateView, self).post(request, *args,
                                                       **kwargs)

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        ctx = dict()
        if "add_question" in request.POST:
            cb_answer = request.POST.get("cb_answer", None)
            ctx.update({"cb_answer": cb_answer})
            if form.is_valid():
                self.object = form.save(commit=False)

                kwargs = {"request": request}
                if cb_answer:
                    kwargs.update({"empty_permitted": False})

                formset = QAFormSet(data=request.POST, instance=self.object,
                                    **kwargs)
                if formset.is_valid():
                    self.object.save()
                    form.save_m2m()
                    formset.save()
                    return HttpResponseRedirect(self.get_success_url())
                ctx.update({"formset": formset})
        elif "add_item" in request.POST:
            i_form = ItemForm(data=request.POST, request=request,
                              prefix="item")
            if i_form.is_valid():
                item = i_form.save()
            else:
                ctx.update({"i_form": i_form, "show": 1})
            initial = dict()
            for name, field in form.fields.items():
                initial.update({name: request.POST.get(name)})
            form = form_class(initial=initial, request=request)

        ctx.update({"form": form})
        return self.render_to_response(self.get_context_data(**ctx))

    def get_context_data(self, **kwargs):
        context = super(ContentCreateView, self).get_context_data(**kwargs)
        if self.model is not Question:
            return context
        POST = self.request.POST
        if "formset" not in context:
            formset = QAFormSet(data=POST, request=self.request) if POST \
                else QAFormSet(request=self.request)
            context.update({"formset": formset})
        if "i_form" not in context:
            i_form = ItemForm(data=POST, request=self.request, prefix="item") \
                if POST else ItemForm(request=self.request, prefix="item")
            context.update({"i_form": i_form})
        err = any(item for item in context.get("formset").errors)
        context.update({"formset_errors": err})
        return context


class ContentUpdateView(ContentView, ContentFormMixin, UpdateView):

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.model == Item:
            add_images(request, **kwargs)
        return super(ContentUpdateView, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ContentUpdateView, self).get_context_data(**kwargs)
        if self.model == Item:
            album = get_album(self.object)
            images = search_images(self.object.name)
            context.update({'img_album': json.dumps(album),
                            'img_search': json.dumps(images)})
        return context


class ContentDetailView(ContentView, NextMixin, DetailView, FormMixin,
                        ProcessFollowView, ProcessVoteView):

    messages = {
        "created": {
            "level": messages.SUCCESS,
            "text": _("Thanks %(user)s, %(object)s successfully created.")
        },
        "failed": {
            "level": messages.WARNING,
            "text": _("Warning %(user)s, %(object)s form is invalid.")
        },
    }

    def get_context_data(self, **kwargs):
        context = super(ContentDetailView, self).get_context_data(**kwargs)
        request = self.request
        POST, user = [request.POST, request.user]
        public_query = Q(status=Content.STATUS.public)
        if self.model == Item:
            item = context.get("item")
            item_query = Q(items__id=item.id)
            content_qs = Content.objects.filter(public_query & item_query)
            querysets = {
                "questions": content_qs.filter(question__isnull=False),
            }
            # feat_qs = content_qs.filter(feature__isnull=False)
            # querysets.update({
            #     "feat_pos": feat_qs.filter(feature__positive=True),
            #     "feat_neg": feat_qs.filter(feature__positive=False),
            #     "links": content_qs.filter(link__isnull=False),
            # })

            contents = dict()
            for key, queryset in querysets.items():
                contents.update({key: get_sorted_queryset(queryset, user)})

            initial = {"status": Content._meta.get_field("status").default,
                       "items": item.id}
            q_form = QuestionForm(data=POST, request=request) if "question" \
                in POST else QuestionForm(initial=initial, request=request)
            q_id = int(POST["question_id"]) \
                if "answer" in POST and "question_id" in POST else -1

            media = None
            for q in contents.get("questions").get("queryset"):
                q.answer_form = AnswerForm(request=request) \
                    if q.id != q_id else AnswerForm(data=POST, request=request)
                answer_qs = Content.objects.filter(
                    Q(answer__question__id=q.id) & public_query)
                q.answers = get_sorted_queryset(answer_qs, user)
                if not media:
                    media = q.answer_form.media
            context.update(contents)
            context.update({"media": media})

            p_list = Profile.objects.filter(skills__in=self.object.tags.all())
            context.update({"q_form": q_form, "prof_list": p_list.distinct()})

            # Linked affiliated products
            store_prods = item.affiliationitem_set.select_related()
            if store_prods:
                store_prods = store_prods.order_by("price")
                cheapest_prod = store_prods[0]
                ean_set = set(store_prods.values_list("ean", flat=True))
                store_prods_by_ean = dict()
                for ean in ean_set:
                    store_prods_by_ean.update({
                        ean: store_prods.filter(ean=ean)
                    })
                context.update({
                    "store_prods_by_ean": store_prods_by_ean,
                    "cheapest_prod": cheapest_prod
                })

            albums = self.object.node().graph.image_set
            if albums:
                # This is a way to order by values of an hstore key
                images = albums[0].successors.extra(
                    select={"order": "content_relation.data -> 'order'"},
                    order_by=['order', ]
                )
                context.update({'album': images})

        elif self.model == Question:
            q = context.get("question")
            q.answer_form = AnswerForm(POST, request=request) \
                if "answer" in POST else AnswerForm(request=request)
            q.score = Vote.objects.get_score(q.content_ptr)
            q.vote = Vote.objects.get_for_user(q.content_ptr, user)

            answer_qs = Content.objects.filter(
                Q(answer__question__id=q.id) & public_query)
            q.answers = get_sorted_queryset(answer_qs, user)

            tag_ids = q.items.all().values_list("tags__id", flat=True)
            p_list = Profile.objects.filter(skills__id__in=tag_ids).distinct()
            context.update({"question": q, "prof_list": p_list})

            qs = Content.objects.filter(question__items__in=q.items.all())
            qs = qs.exclude(id=q.id)
            qs_ordered = generic_annotate(qs, Vote, Sum('votes__vote'))
            qs_ordered = qs_ordered.order_by("-score").select_subclasses()
            context.update({
                "question": q, "prof_list": p_list, "item_list": q.items.all(),
                "related_questions": {
                    _("Top related questions"): qs_ordered[:3],
                    _("Latest related questions"): qs.select_subclasses()[:3]
                }
            })
        return context

    def form_invalid(self, form):
        self.object = self.get_object()
        messages.add_message(self.request,
            self.messages["failed"]["level"],
            self.messages["failed"]["text"] % {
                "user": user_display(self.request.user),
                "object": form._meta.model._meta.verbose_name
            }
        )
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form, request, **kwargs):
        self.object = form.save(**kwargs)
        form.save_m2m()
        messages.add_message(self.request,
            self.messages["created"]["level"],
            self.messages["created"]["text"] % {
                "user": user_display(self.request.user),
                "object": self.object._meta.verbose_name
            }
        )
        if self.object._meta.object_name == "Answer":
            mail_question_author(request.META.get('HTTP_HOST'), self.object)
        return HttpResponseRedirect(self.get_success_url())

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if "ask" in request.POST:
            obj = load_object(request)
            return process_asking_for_help(request, obj, request.path)
        elif "question" in request.POST or "answer" in request.POST:
            Form = QuestionForm if "question" in request.POST else AnswerForm
            form = Form(data=request.POST, request=request)
            if form.is_valid():
                return self.form_valid(form, request, **kwargs)
            else:
                return self.form_invalid(form)
        else:
            return super(ContentDetailView, self).post(request, *args,
                                                       **kwargs)

    def get_success_url(self):
        if self.success_url:
            url = self.success_url % self.object.__dict__
        else:
            try:
                url = self.object.get_absolute_url()
            except AttributeError:
                raise ImproperlyConfigured(
                    "No URL to redirect to. Either provide a url or define"
                    " a get_absolute_url method on the Model."
                )
        return url


class SearchMixin(object):

    def post(self, request, *args, **kwargs):
        search = request.POST.get("item_search", "")
        if not search:
            return super(SearchMixin, self).post(request, *args, **kwargs)

        item_list = Item.objects.filter(name=search)
        tag_list = Tag.objects.filter(name=search)
        if item_list.count() == 1:
            response = item_list[0].get_absolute_url()
        elif tag_list.count() == 1:
            response = reverse("tagged_items", args=[tag_list[0].slug])
        else:
            response = "%s?q=%s" % (reverse("content_search"), search)
        return HttpResponseRedirect(response)


class ContentListView(ContentView, SearchMixin, ListView):

    model = Item
    template_name = "items/item_list_image.html"
    paginate_by = 9

    def get_queryset(self):
        qs = super(ContentListView, self).get_queryset()
        if "tag_slug" in self.kwargs:
            self.tag = get_object_or_404(Tag, slug=self.kwargs.get("tag_slug"))
            qs = qs.filter(tags=self.tag)
        self.search_terms = self.request.GET.get("q", "")
        if self.search_terms:
            self.template_name = "items/item_list_text.html"
            qs = get_search_results(qs, self.search_terms, ["name"])
            return qs
        POST = self.request.POST
        self.sort_order = POST.get("sort_products")\
            if "sort_products" in POST else "-pub_date"
        field = "content__question__id"
        qs = list(qs.annotate(score=Count(field)).order_by("-score"))\
            if self.sort_order == "popular" else qs.order_by(self.sort_order)
        return qs

    def get_context_data(self, **kwargs):
        context = super(ContentListView, self).get_context_data(**kwargs)
        context.update({"media": ChosenSelect().media})
        for attr in ["tag", "search_terms", "sort_order"]:
            context.update({attr: getattr(self, attr, "")})
        if not "object_list" in context:
            return context
        objs = context.get("object_list")
        nb_items = objs.count() if type(objs) is QuerySet else len(objs)
        if nb_items == 0:
            return context
        qs = Content.objects.filter(question__items__in=objs).distinct()
        qss = generic_annotate(qs, Vote, Sum('votes__vote')).order_by("-score")
        rq = SortedDict()
        rq.update({_("Top related questions"): qss.select_subclasses()[:3]})
        rq.update({_("Latest related questions"): qs.select_subclasses()[:3]})
        context.update({"related_questions": rq})
        return context

    def post(self, request, *args, **kwargs):
        if "tag_slug" in self.kwargs and "skills" in request.POST:
            tag = get_object_or_404(Tag, slug=self.kwargs.get("tag_slug"))
            prof = request.user.get_profile()
            prof.skills.add(tag) if request.POST.get("skills") == "add" \
                else prof.skills.remove(tag)
        return super(ContentListView, self).post(request, *args, **kwargs)


class ContentDeleteView(ContentView, NextMixin, DeleteView):

    template_name = "items/confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not request.user.has_perm("can_manage", self.object):
            raise PermissionDenied
        success_url = self.get_success_url(request)
        self.object.delete()
        return HttpResponseRedirect(success_url)

    def get_success_url(self, request):
        if self.success_url:
            success_url = self.success_url % self.object.__dict__
        elif self.model.__name__ == "Item":
            success_url = reverse("item_index")
        elif "success_url" in request.GET:
            success_url = request.GET.get("success_url")
        else:
            success_url = None

        obj = self.object
        if success_url != obj.get_absolute_url() and success_url is not None:
            return success_url
        else:
            try:
                return obj.items.all()[0].get_absolute_url()
            except:
                pass
        raise ImproperlyConfigured
