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
from django.views.generic.edit import ModelFormMixin

from django.contrib.auth.decorators import login_required
from django.contrib import messages

from account.utils import user_display
from generic_aggregation import generic_annotate
from taggit.models import Tag
from voting.models import Vote

from content.transition import add_images, get_album
from items.models import Item, Content, Question, Link, Feature
from items.forms import QuestionForm, AnswerForm, ItemForm, QAFormSet
from profiles.models import Profile
from utils.apiservices import search_images
from utils.mailtools import process_asking_for_help
from utils.follow.views import FollowMixin
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
        if "next" in request.GET:
            kwargs.update({"next": request.GET.get("next")})
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
            status = self.request.POST.get(field, None)
            if status:
                kwargs.update({"status": int(status)})
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
        kwargs.update({"status": Content.STATUS})
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
            initial = dict()
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
        self.success_url = url + "?next=" + next if url and next else url

        return super(ContentCreateView, self).get_success_url()


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


class ContentDetailView(ContentView, DetailView, ModelFormMixin,
                        FollowMixin, ProcessVoteView):

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

            contents = dict()
            for key, queryset in querysets.items():
                contents.update({key: get_sorted_queryset(queryset, user)})

            initial = {"items": item.id,
                       "parents": QuestionForm.PARENTS.products}
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
                if "answer" in POST else AnswerForm(request)
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

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        POST = request.POST
        if "ask" in POST:
            obj = load_object(request)
            return process_asking_for_help(request, obj, request.path)
        elif "question" in POST or "answer" in POST:
            Form = QuestionForm if "question" in POST else AnswerForm
            form = Form(request, data=POST)
            if form.is_valid():
                display_message("created", self.request,
                                Form._meta.model._meta.verbose_name)
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
        elif "edit_about" in POST:
            about = POST.get("about", "")
            profile = request.user.get_profile()
            profile.about = about
            profile.save()
            display_message("about", self.request)
            return HttpResponseRedirect(request.path)
        else:
            return super(ContentDetailView, self).post(request, *args,
                                                       **kwargs)


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


class ContentListView(ContentView, SearchMixin, MultiTemplateMixin, ListView):

    model = Item
    template_name = "items/item_list_image.html"
    paginate_by = 9
    sort_order = "-pub_date"

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
        field = "content__question__id"
        qs = list(qs.annotate(score=Count(field)).order_by("-score"))\
            if self.sort_order == "popular" else qs.order_by(self.sort_order)
        return qs

    def get_context_data(self, **kwargs):
        context = super(ContentListView, self).get_context_data(**kwargs)
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

        ###### Seb's : for trial template on tags page
        if "tag_slug" in self.kwargs:
            self.tag = get_object_or_404(Tag, slug=self.kwargs.get("tag_slug"))

            questions_on_tag = Question.objects.filter(tags=self.tag)[:3]
            context.update({"questions_on_tag": questions_on_tag})
            ### To do : sort these questions by vote

            items_wi_tag = Item.objects.filter(tags=self.tag)
            questions_on_items_wi_tag = Question.objects.filter(items__in=items_wi_tag)[:3]
            context.update({"questions_on_items_wi_tag": questions_on_items_wi_tag})
            ## To Do : sort these questions by vote

            unanswered_q_wi_tag = Question.objects.annotate(
                    score=Count("answer")
                ).filter( Q(score__lte=0),
                    Q(tags=self.tag) | Q(items__in=items_wi_tag)
                )[:3]
            context.update({"unanswered_q_wi_tag": unanswered_q_wi_tag})
        ###### end of Seb's
        return context

    def post(self, request, *args, **kwargs):
        if "tag_slug" in self.kwargs and "skills" in request.POST:
            tag = get_object_or_404(Tag, slug=self.kwargs.get("tag_slug"))
            prof = request.user.get_profile()
            prof.skills.add(tag) if request.POST.get("skills") == "add" \
                else prof.skills.remove(tag)
            return self.get(request, *args, **kwargs)
        elif "sort_products" in request.POST:
            self.sort_order = self.request.POST.get("sort_products")
            return self.get(request, *args, **kwargs)
        return super(ContentListView, self).post(request, *args, **kwargs)


class ContentDeleteView(ContentView, DeleteView):

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
