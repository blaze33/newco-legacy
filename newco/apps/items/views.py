import json

from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Count, Sum
from django.db.models.loading import get_model
from django.http import HttpResponseRedirect, HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.datastructures import SortedDict
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View, ListView, CreateView, DetailView
from django.views.generic import UpdateView, DeleteView
from django.views.generic.edit import FormMixin

from django.contrib.auth.decorators import login_required

from taggit.models import Tag

from affiliation import CURRENCIES
from content.transition import add_images, get_album
from items import STATUSES
from items.forms import QuestionForm, AnswerForm, ItemForm, QAFormSet
from items.forms import PartialQuestionForm
from items.models import Item, Content, Question
from profiles.models import Profile
from utils.apiservices import search_images
from utils.follow.views import FollowMixin
from utils.voting.views import VoteMixin
from utils.messages import add_message, render_messages
from utils.multitemplate.views import MultiTemplateMixin
from utils.help.views import AskForHelpMixin
from utils.views.tutorial import TutorialMixin
from utils.tools import fill_product_list_by_tag, fill_question_list_by_tag

app_name = "items"


class ContentView(TutorialMixin, View):

    def dispatch(self, request, *args, **kwargs):
        if "model_name" in kwargs:
            self.model = get_model(app_name, kwargs["model_name"])
        try:
            self.kwargs = kwargs
            self.object = self.get_object()
            slug = self.object.slug
            if slug and kwargs['slug'] != slug:
                url = self.object.get_absolute_url()
                return HttpResponsePermanentRedirect(url)
        except:
            pass  # no get_object method, we're not accessing a single object.
        if "next" in request.GET:
            self.next = request.GET.get("next")
            kwargs.update({"next": self.next})
        self.success_url = request.POST.get("next", None)
        return super(ContentView, self).dispatch(request, *args, **kwargs)


class ContentFormMixin(object):

    object = None

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if "model_name" in kwargs:
            form_class_name = self.model._meta.object_name + "Form"
            if form_class_name in globals():
                self.form_class = globals()[form_class_name]
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
        POST = request.POST

        if self.model == Item and ("add_links" in POST or "del_links" in POST
                                   or "store_search" in POST):
            if "add_links" in POST and self.object:
                form.link_aff(self.object)
            if "del_links" in POST and self.object:
                form.unlink_aff(self.object)
            if "store_search" in POST:
                form.stores_search()
            return self.render_to_response(self.get_context_data(form=form))
        elif request.is_ajax() and "add_item" in POST:
            form = ItemForm(data=POST, request=request, prefix="item")
            if form.is_valid():
                item = form.save()
                args = [item._meta.module_name, item.id]
                add_message("object-created", request,
                                model=form._meta.model)
                messages = render_messages(request)
                data = {"id": item.id, "name": item.name, "messages": messages,
                        "next": reverse("item_edit", args=args)}
            else:
                data = "invalid form"
            return HttpResponse(json.dumps(data), mimetype="application/json")
        elif form.is_valid():
            key = "object-updated" if self.object else "object-created"
            add_message(key, request, model=self.model)
            return self.form_valid(form)
        else:
            add_message("form-invalid", request, model=self.model)
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        kwargs.update({"statuses": STATUSES})
        if self.model is Question:
            form = ItemForm(request=self.request, prefix="item")
            kwargs.update({"i_form": form})
        return super(ContentFormMixin, self).get_context_data(**kwargs)

    def get_success_url(self):
        if self.model is Question:
            args = (self.success_url, self.object.get_absolute_url())
            self.success_url = "%s?next=%s" % args if all(args) else args[0]
        return super(ContentFormMixin, self).get_success_url()


class ContentCreateView(ContentView, ContentFormMixin, MultiTemplateMixin,
                        CreateView):

    def post(self, request, *args, **kwargs):
        POST = request.POST
        if self.model is Question and "add_question" in POST:
            form_class = self.get_form_class()
            form = self.get_form(form_class)
            cb_answer = POST.get("cb_answer", None)
            ctx = {"cb_answer": cb_answer}
            if form.is_valid():
                self.object = form.save(commit=False)
                kwargs = {"request": request, "status": self.object.status}
                if cb_answer:
                    kwargs.update({"empty_permitted": False})
                formset = QAFormSet(data=POST, instance=self.object, **kwargs)
                if formset.is_valid():
                    add_message("object-created", request, model=self.model)
                    self.object.save()
                    form.save_m2m()
                    formset.save()
                    return HttpResponseRedirect(self.get_success_url())
                else:
                    add_message("form-invalid", request,
                                    model=formset.model)
                ctx.update({"formset": formset})
            else:
                add_message("form-invalid", request, model=self.model)
            ctx.update({"form": form})
            return self.render_to_response(self.get_context_data(**ctx))

        return super(ContentCreateView, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ContentCreateView, self).get_context_data(**kwargs)
        if self.model is not Question:
            return context
        POST = self.request.POST
        if "formset" not in context:
            formset = QAFormSet(data=POST, request=self.request) if POST \
                else QAFormSet(request=self.request)
            context.update({"formset": formset})
        err = any(item for item in context.get("formset").errors)
        context.update({"formset_errors": err})
        return context

    def get_success_url(self):
        if self.model == Item and "edit" in self.request.POST:
            args = [self.object._meta.module_name, self.object.id]
            self.success_url = reverse("item_edit", args=args)
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


# Can't directly subclass FormMixin because of get_context_data.
# Won't be an issue in 1.5
class QuestionFormMixin(object):

    items = []
    tags = []

    def form_invalid(self, form):
        if "question" not in self.request.POST:
            return super(QuestionFormMixin, self).form_invalid(form)
        return self.render_to_response(self.get_context_data(
            question_form=form))

    def form_valid(self, form):
        if "question" not in self.request.POST:
            return super(QuestionFormMixin, self).form_valid(form)
        question = form.save()
        self.success_url = question.get_absolute_url()
        return HttpResponseRedirect(self.success_url)

    def get_form_kwargs(self):
        kwargs = super(QuestionFormMixin, self).get_form_kwargs()
        kwargs.update({"request": self.request, "prefix": "question"})
        for attr in ["items", "tags"]:
            if getattr(self, attr):
                kwargs.update({attr: getattr(self, attr)})
        return kwargs

    def get_context_data(self, **kwargs):
        form = kwargs.pop("question_form", None)
        if not form:
            form_class = PartialQuestionForm
            form = self.get_form(form_class)
            if "question" not in self.request.POST:
                form.errors.clear()
        kwargs.update({"question_form": form})
        return super(QuestionFormMixin, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        POST = request.POST
        if "question" not in POST:
            return super(QuestionFormMixin, self).post(request, *args,
                                                       **kwargs)
        form_class = PartialQuestionForm
        form = self.get_form(form_class)
        if form.is_valid():
            add_message("object-created", request, model=form._meta.model)
            return self.form_valid(form)
        else:
            add_message("form-invalid", request, model=form._meta.model)
            return self.form_invalid(form)

class RelatedObjectsMixin(object):

    def get_context_data(self, **kwargs):
        context = super(RelatedObjectsMixin, self).get_context_data(**kwargs)
        context.update({"statuses": STATUSES})
        request = self.request
        POST, user = [request.POST, request.user]
        content_qs = Content.objects.can_view(user)
        if self.model == Item:
            item = context.get("item")
            item_related_qs = content_qs.filter(items=item)
            scores, votes = item_related_qs.get_scores_and_votes(user)
            top_products_by_tag={}
            nb_questions_by_tag={}
            top_question_by_tag={}
            ##### We created a list to check all the doublons for products and not display them twice ####
            list_doublons_p = []
            list_doublons_q = []
            for tag in item.tags.all():
                related_products = Item.objects.filter(
                    Q(tags=tag)).exclude(id=item.id).distinct()
            
                top_products = related_products.order_queryset("popular")
                list_products_by_tag=[]
                ##### Loop to find the N first related products && not in list_doublons ####
                nb_products = 2
                fill_product_list_by_tag(list_products_by_tag,nb_products,top_products,list_doublons_p)
                ##### We display only N products per row ####
                top_products_by_tag[tag]=list_products_by_tag[:nb_products]
                
                ##### We created a list to check all the doublons for questions and not display them twice ####
                qs_tags=Tag.objects.all().filter(name=tag)
                self.queryset = Content.objects.questions().filter(tags__in=qs_tags).select_subclasses()
                top_questions = self.queryset.order_queryset("popular")
                
                list_questions_by_tag=[]
                nb_questions = 1
                fill_question_list_by_tag(list_questions_by_tag,nb_questions,top_questions,list_doublons_q,tag,top_question_by_tag)
                
#                nb_questions = self.queryset.count()
#                nb_questions_by_tag[tag]=nb_questions
                kwargs.update({"top_question_by_tag": top_question_by_tag, "top_products_by_tag": top_products_by_tag })
        return super(RelatedObjectsMixin, self).get_context_data(**kwargs)


class ContentDetailView(ContentView, AskForHelpMixin, QuestionFormMixin, RelatedObjectsMixin,
                        DetailView, FormMixin, FollowMixin, VoteMixin):

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.experts = self.get_experts()
        kwargs = {"object": self.object, "experts": self.experts}
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

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
            questions = item_related_qs.questions().prefetch_related(
                "author__reputation", "answer_set__author__reputation"
            ).order_queryset("popular", scores)

            q_id = -1
            if "answer" in POST and "question_id" in POST:
                q_id = int(POST.get("question_id"))
                context.update({"q_id": q_id})

            media = None
            for q in questions:
                q.answer_form = AnswerForm(request=request) \
                    if q.id != q_id else AnswerForm(data=POST, request=request)
                if not media:
                    media = q.answer_form.media
                    
            context.update({"questions": questions, "scores": scores,
                            "votes": votes, "media": media})

            # Linked affiliated products
            products = item.affiliationitem_set.select_related("store")
            if products:
                context.update({
                    "store_products": products,
                    "cheapest": products.get_cheapest(CURRENCIES.euro)})

            albums = self.object.node.graph.image_set
            if albums:
                # This is a way to order by values of an hstore key
                images = albums[0].successors.extra(
                    select={"order": "content_relation.data -> 'order'"},
                    order_by=['order', ]
                )
                context.update({'album': images})

        elif self.model == Question:
            # TODO: override get_object?
            q = Content.objects.filter(
                id=context["question"].id).prefetch_related(
                    "answer_set__author__reputation").select_subclasses().get()

            q.answer_form = AnswerForm(request, data=POST) \
                if "answer" in POST else AnswerForm(request)

            qna_qs = content_qs.filter(Q(id=q.id) | Q(answer__question=q))
            scores, votes = qna_qs.get_scores_and_votes(user)
            context.update({"question": q, "scores": scores, "votes": votes})

            tag_ids = q.items.all().values_list("tags__id", flat=True)
            experts = Profile.objects.filter(skills__id__in=tag_ids).distinct()

            related_questions = Content.objects.questions().filter(
                Q(items__in=q.items.all()) | Q(tags__in=q.tags.all())
            ).exclude(id=q.id).distinct()
            top_questions = related_questions.order_queryset("popular")
            related_questions = related_questions.select_subclasses()

            context.update({"experts": experts, "related_questions": {
                _("Top related questions"): top_questions[:3],
                _("Latest related questions"): related_questions[:3]
            }})
        return context

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.experts = self.get_experts()
        self.items = [self.object]
        POST = request.POST
        if "answer" in POST:
            status = int(POST.get("answer"))
            form = AnswerForm(request, data=POST, status=status)
            if form.is_valid():
                add_message("object-created", request, model=form._meta.model)
                answer = form.save()
                self.success_url = answer.get_absolute_url()
                return self.form_valid(form)
            else:
                add_message("form-invalid", request, model=form._meta.model)
                return self.form_invalid(form)
        elif request.is_ajax and "edit_about" in POST:
            about = POST.get("about", "")
            ## DJANGO 1.5: use defer and save only about field
            profile = request.user.get_profile()
            toggle = bool(profile.about) != bool(about)
            profile.about = about
            profile.save()
            add_message("about", request)
            messages = render_messages(request)
            data = {"about": about, "messages": messages, "result": "success",
                    "toggle": toggle}
            return HttpResponse(json.dumps(data), mimetype="application/json")
        else:
            return super(ContentDetailView, self).post(request, *args,
                                                       **kwargs)

    def get_experts(self):
        tag_ids = list(self.object.tags.values_list("id", flat=True))
        if self.object.__class__ is Question:
            tag_ids.extend(self.object.items.values_list("tags", flat=True))
        return Profile.objects.filter(skills__id__in=tag_ids).order_by(
            "-user__reputation__reputation_incremented").distinct()

DEFAULT_CATGORY = "products"
DEFAULT_FILTERS = {"products": "popular", "questions": "popular"}
MODELS = {"products": Item, "questions": Content}


class ContentListView(ContentView, MultiTemplateMixin, AskForHelpMixin,
                      QuestionFormMixin, ListView, FormMixin, VoteMixin):

    paginate_by = 9

    def dispatch(self, request, *args, **kwargs):
        self.tag = get_object_or_404(Tag, slug=kwargs.get("tag_slug", ""))
        self.experts = self.get_experts()
        self.cat = kwargs.get("cat", DEFAULT_CATGORY)
        self.model = MODELS[self.cat]
        self.template_name = "items/item_list_%s.html" % self.cat
        self.qs_option = request.GET.get("qs_option",
                                         DEFAULT_FILTERS[self.cat])
        return super(ContentView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = super(ContentListView, self).get_queryset()
        if self.cat == "products":
            qs = qs.filter(tags=self.tag)
            field = "content__question__id"
            qs = qs.annotate(score=Count(field)).order_by("-score") \
                if self.qs_option == "popular" else qs.order_by(self.qs_option)
            msg = _("No product with tag {tag}")
        elif self.cat == "questions":
            qs = qs.filter(tags=self.tag)
            msg = _("No question with tag {tag} yet. "
                    "Be the first to ask one!")
            self.scores, self.votes = qs.get_scores_and_votes(
                self.request.user)
            qs = qs.questions().order_queryset(self.qs_option, self.scores)

        tpl = "tags/_tag_display.html"
        print render_to_string(tpl, {"tag": self.tag})
        self.empty_msg = mark_safe(
            msg.format(tag=render_to_string(tpl, {"tag": self.tag})))
        return qs

    def get_context_data(self, **kwargs):
        if "object_list" not in kwargs:
            kwargs.update({"object_list": self.object_list})
        context = super(ContentListView, self).get_context_data(**kwargs)
        for attr in ["tag", "qs_option", "cat", "scores", "votes",
                     "empty_msg"]:
            if hasattr(self, attr):
                context.update({attr: getattr(self, attr)})
        if self.model is Item:
            context.get("object_list").fetch_images()
        else:
            context.update({"item_list": Item.objects.filter(tags=self.tag)})
            context.get("item_list").fetch_images()
        context.update({"experts": self.get_experts})
        return context

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        self.tags = [self.tag]
        if "toggle-skill" in request.POST:
            return self.toggle_skill(request, *args, **kwargs)
        return super(ContentListView, self).post(request, *args, **kwargs)

    def get_experts(self):
        return Profile.objects.filter(skills=self.tag).order_by(
            "-user__reputation__reputation_incremented").distinct()

    @method_decorator(login_required)
    def toggle_skill(self, request, *args, **kwargs):
        profile = request.user.get_profile()
        if self.tag in profile.skills.all():
            profile.skills.remove(self.tag.name)
            add_message("skill-removed", request, tag=self.tag)
        else:
            profile.skills.add(self.tag)
            add_message("skill-added", request, tag=self.tag)

        if request.is_ajax():
            data = {"messages": render_messages(request)}
            return HttpResponse(json.dumps(data), mimetype="application/json")
        else:
            return HttpResponseRedirect(request.path)


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
