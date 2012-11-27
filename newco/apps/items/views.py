import json

from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Count
from django.db.models.loading import get_model
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.datastructures import SortedDict
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View, ListView, CreateView, DetailView
from django.views.generic import UpdateView, DeleteView
from django.views.generic.edit import ModelFormMixin

from django.contrib.auth.decorators import login_required
from django.contrib import messages

from account.utils import user_display
from taggit.models import Tag
from voting.models import Vote

from content.transition import add_images, get_album
from items import STATUSES
from items.forms import QuestionForm, AnswerForm, ItemForm, QAFormSet
from items.forms import PartialQuestionForm
from items.models import Item, Content, Question, Link, Feature
from profiles.models import Profile
from utils.apiservices import search_images
from utils.mailtools import process_asking_for_help
from utils.follow.views import FollowMixin
from utils.tools import load_object
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
        if "next" in request.GET:
            self.next = request.GET.get("next")
            kwargs.update({"next": self.next})
        self.success_url = request.POST.get("next", None)
        return super(ContentView, self).dispatch(request, *args, **kwargs)


class ContentFormMixin(object):

    object = None

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ContentFormMixin, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(ContentFormMixin, self).get_form_kwargs()
        kwargs.update({"request": self.request})
        for field in ["add_question", "add_answer"]:
            if field in self.request.POST:
                kwargs.update({"status": int(self.request.POST.get(field))})
                break
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
            msg = "updated" if self.object else "created"
            display_message(msg, self.request, self.model._meta.verbose_name)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        kwargs.update({"statuses": STATUSES})
        return super(ContentFormMixin, self).get_context_data(**kwargs)


class ContentCreateView(ContentView, ContentFormMixin, MultiTemplateMixin,
                        CreateView):

    def post(self, request, *args, **kwargs):
        if self.model is not Question:
            return super(ContentCreateView, self).post(request, *args,
                                                       **kwargs)

        POST = request.POST
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        cb_answer = POST.get("cb_answer", None)
        ctx = {"cb_answer": cb_answer}
        if "add_question" in POST:
            if form.is_valid():
                self.object = form.save(commit=False)
                kwargs = {"request": request, "status": self.object.status}
                if cb_answer:
                    kwargs.update({"empty_permitted": False})
                formset = QAFormSet(data=POST, instance=self.object, **kwargs)
                if formset.is_valid():
                    display_message("created", self.request,
                                    self.object._meta.verbose_name)
                    self.object.save()
                    form.save_m2m()
                    formset.save()
                    next = self.object.get_absolute_url()
                    return HttpResponseRedirect(self.get_success_url(next))
                ctx.update({"formset": formset})
        elif request.is_ajax() and "add_item" in POST:
            i_form = ItemForm(data=POST, request=request, prefix="item")
            if i_form.is_valid():
                item = i_form.save()
                args = [item._meta.module_name, item.id]
                response_data = {"id": item.pk,
                                 "name": item.name,
                                 "next": reverse("item_edit", args=args)}
            else:
                response_data = 'invalid form'
            return HttpResponse(json.dumps(response_data), mimetype="application/json")
        elif "add_item" in POST:
            i_form = ItemForm(data=POST, request=request, prefix="item")
            if i_form.is_valid():
                item = i_form.save()
                display_message("created", self.request,
                                item._meta.verbose_name)
                args = [item._meta.module_name, item.id]
                ctx.update({"next": reverse("item_edit", args=args)})
            else:
                ctx.update({"i_form": i_form, "show": 1})
            initial = {}
            for name, field in form.fields.items():
                val = POST.get(name) if name != "items" else POST.getlist(name)
                initial.update({name: val})
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
            i_form = ItemForm(request=self.request, prefix="item")
            context.update({"i_form": i_form})
        err = any(item for item in context.get("formset").errors)
        context.update({"formset_errors": err})
        return context

    def get_success_url(self, next=None):
        if self.model == Item and "edit" in self.request.POST:
            args = [self.object._meta.module_name, self.object.id]
            self.success_url = reverse("item_edit", args=args)
        url = self.success_url
        self.success_url = "%s?next=%s" % (url, next) if url and next else url

        return super(ContentCreateView, self).get_success_url()


class ContentUpdateView(ContentView, ContentFormMixin, UpdateView):

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.model == Item:
            add_images(request, **kwargs)
        return super(ContentUpdateView, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        if hasattr(self, "next"):
            kwargs.update({"next": self.next})
        context = super(ContentUpdateView, self).get_context_data(**kwargs)
        if self.model == Item:
            album = get_album(self.object)
            images = search_images(self.object.name)
            context.update({'img_album': json.dumps(album),
                            'img_search': json.dumps(images)})
        return context


class ContentDetailView(ContentView, DetailView, ModelFormMixin,
                        FollowMixin, ProcessVoteView):

    def get_context_data(self, **kwargs):
        context = super(ContentDetailView, self).get_context_data(**kwargs)
        context.update({"statuses": STATUSES})
        request = self.request
        POST, user = [request.POST, request.user]
        content_qs = Content.objects.can_view(user)
        if self.model == Item:
            item = context.get("item")
            item_related_qs = content_qs.filter(items=item)
            scores, votes = item_related_qs.get_scores_and_votes(user)
            question_qs = item_related_qs.filter(
                question__isnull=False)
            questions = question_qs.order_queryset("popular", scores)

            q_form = PartialQuestionForm(request, item, data=POST) \
                if "question" in POST else PartialQuestionForm(request, item)
            q_id = -1
            if ("answer" in POST or "edit_about" in POST) \
                    and "question_id" in POST:
                q_id = int(POST.get("question_id"))
                context.update({"q_id": q_id})

            media = None
            for q in questions:
                q.answer_form = AnswerForm(request=request) \
                    if q.id != q_id else AnswerForm(data=POST, request=request)
                if not media:
                    media = q.answer_form.media

            p_qs = Profile.objects.filter(skills__in=item.tags.all())

            context.update({
                "questions": questions, "scores": scores, "votes": votes,
                "media": media, "q_form": q_form, "profile_qs": p_qs.distinct()
            })

            # Linked affiliated products
            store_prods = item.affiliationitem_set.select_related()
            if store_prods:
                store_prods = store_prods.order_by("price")
                cheapest_prod = store_prods[0]
                ean_set = set(store_prods.values_list("ean", flat=True))
                store_prods_by_ean = {}
                for ean in ean_set:
                    store_prods_by_ean.update({
                        ean: store_prods.filter(ean=ean)
                    })
                context.update({
                    "store_prods_by_ean": store_prods_by_ean,
                    "cheapest_prod": cheapest_prod
                })

            albums = self.object.node.graph.image_set
            if albums:
                # This is a way to order by values of an hstore key
                images = albums[0].successors.extra(
                    select={"order": "content_relation.data -> 'order'"},
                    order_by=['order', ]
                )
                context.update({'album': images})

        elif self.model == Question:
            q = context.get("question")
            q.answer_form = AnswerForm(request, data=POST) \
                if "answer" in POST or "edit_about" in POST \
                else AnswerForm(request)

            qna_qs = content_qs.filter(Q(id=q.id) | Q(answer__question=q))
            scores, votes = qna_qs.get_scores_and_votes(user)
            context.update({"question": q, "scores": scores, "votes": votes})

            tag_ids = q.items.all().values_list("tags__id", flat=True)
            p_qs = Profile.objects.filter(skills__id__in=tag_ids).distinct()

            related_questions = Content.objects.filter(
                question__items__in=q.items.all()).exclude(id=q.id)
            top_questions = related_questions.order_queryset("popular")
            related_questions = related_questions.select_subclasses()

            context.update({"profile_qs": p_qs, "related_questions": {
                _("Top related questions"): top_questions[:3],
                _("Latest related questions"): related_questions[:3]
            }})
        return context

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        POST = request.POST
        if "ask" in POST:
            obj = load_object(request)
            return process_asking_for_help(request, obj, request.path)
        elif "question" in POST or "answer" in POST:
            if "question" in POST:
                form = PartialQuestionForm(request, self.object, data=POST)
            else:
                status = int(POST.get("answer"))
                form = AnswerForm(request, data=POST, status=status)
            if form.is_valid():
                display_message("created", self.request,
                                form._meta.model._meta.verbose_name)
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
        elif "edit_about" in POST:
            about = POST.get("about", "")
            profile = request.user.get_profile()
            profile.about = about
            profile.save()
            display_message("about", self.request)
            return self.render_to_response(self.get_context_data())
        else:
            return super(ContentDetailView, self).post(request, *args,
                                                       **kwargs)


class ContentListView(ContentView, MultiTemplateMixin, ListView):

    paginate_by = 9
    qs_option = "-pub_date"

    def get(self, request, *args, **kwargs):
        self.tag = get_object_or_404(Tag, slug=self.kwargs.get("tag_slug", ""))
        self.cat = kwargs.get("cat", "home")
        self.template_name = "items/item_list_%s.html" % self.cat
        self.qs_option = self.request.GET.get("qs_option", self.qs_option)

        if self.cat == "home" or self.cat == "products":
            self.model, self.pill = [Item, kwargs.get("pill", "browse")]
            self.queryset = Item.objects.filter(tags=self.tag)
            msg = _("No products with tag %s")
        elif self.cat == "questions":
            self.model, self.pill = [Question, kwargs.get("pill", "tag")]
            self.queryset = Content.objects.filter(question__isnull=False)
            if self.pill == "tag":
                self.queryset = self.queryset.filter(tags=self.tag)
                msg = _("No questions with tag %s")
            elif self.pill == "products":
                item_ids = Item.objects.filter(tags=self.tag).values_list(
                    "id", flat=True)
                self.queryset = self.queryset.filter(items__in=item_ids)
                msg = _("No questions about products with tag %s")

        tpl = "tags/_tag_display.html"
        self.empty_msg = mark_safe(
            msg % render_to_string(tpl, {"tag": self.tag}))
        return super(ContentListView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        qs = super(ContentListView, self).get_queryset()
        if self.cat == "products":
            field = "content__question__id"
            qs = qs.annotate(score=Count(field)).order_by("-score") \
                if self.qs_option == "popular" else qs.order_by(self.qs_option)
        elif self.cat == "questions":
            self.scores = qs.get_scores()
            qs = qs.order_queryset(self.qs_option, self.scores)
        return qs

    def get_context_data(self, **kwargs):
        context = super(ContentListView, self).get_context_data(**kwargs)
        for attr in ["tag", "qs_option", "cat", "pill", "scores", "empty_msg"]:
            if hasattr(self, attr):
                context.update({attr: getattr(self, attr)})
        if self.cat == "home" and context.get("object_list"):
            related_questions = Content.objects.filter(
                question__items__in=context.get("object_list")).distinct()
            top_questions = related_questions.order_queryset("popular")
            related_questions = related_questions.select_subclasses()

            context.update({"related_questions": SortedDict({
                _("Top related questions"): top_questions[:3],
                _("Latest related questions"): related_questions[:3]
            })})
        if self.model is Item:
            context.get("object_list").fetch_images()
        else:
            context.update({"item_list": Item.objects.filter(tags=self.tag)})
            context.get("item_list").fetch_images()
        return context

    def post(self, request, *args, **kwargs):
        if "skills" in request.POST:
            tag = get_object_or_404(Tag, slug=self.kwargs.get("tag_slug", ""))
            profile = request.user.get_profile()
            profile.skills.add(tag) if request.POST.get("skills") == "add" \
                else profile.skills.remove(tag)
            return self.get(request, *args, **kwargs)
        return super(ContentListView, self).post(request, *args, **kwargs)


class ContentDeleteView(ContentView, DeleteView):

    template_name = "items/confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not request.user.has_perm("can_manage", self.object):
            raise PermissionDenied
        self.object.delete()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        if hasattr(self, "next"):
            kwargs.update({"next": self.next})
        return super(ContentDeleteView, self).get_context_data(**kwargs)

    def get_success_url(self):
        if self.success_url:
            return self.success_url
        else:
            return "/"


MESSAGES = {
    "created": {
        "level": messages.SUCCESS,
        "text": _("Thanks %(user)s, %(object_name)s successfully created.")
    },
    "updated": {
        "level": messages.INFO,
        "text": _("Thanks %(user)s, %(object_name)s successfully updated.")
    },
    "about": {
        "level": messages.INFO,
        "text": _("Thanks %(user)s, your bio has been successfully updated.")
    },
    "failed": {
        "level": messages.ERROR,
        "text": _("Warning %(user)s, %(object_name)s form is invalid.")
    },
}


def display_message(msg_type, request, object_name=""):
    messages.add_message(
        request, MESSAGES[msg_type]["level"],
        MESSAGES[msg_type]["text"] % {
            "user": user_display(request.user),
            "object_name": object_name
        }
    )
