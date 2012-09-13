import json

from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.db.models.loading import get_model
from django.db.models import Q, Sum
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View, ListView, CreateView, DetailView
from django.views.generic import UpdateView, DeleteView
from django.views.generic.base import RedirectView
from django.views.generic.edit import FormMixin

from django.contrib.auth.decorators import login_required
from django.contrib import messages

from account.utils import user_display
from chosen.forms import ChosenSelect
from generic_aggregation import generic_annotate
from taggit.models import Tag
from voting.models import Vote

from content.transition import add_images, get_album, sync_products
from items.models import Item, Content, Question, Link, Feature
from items.forms import QuestionForm, AnswerForm, ItemForm
from items.forms import LinkForm, FeatureForm
from profiles.models import Profile
from utils.apiservices import search_images
from utils.asktools import process_asking
from utils.follow.views import ProcessFollowView
from utils.tools import get_query, load_object
from utils.vote.views import ProcessVoteView

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
            form = self.form_class(**{"request": request})
        else:
            form_class = self.get_form_class()
            form = self.get_form(form_class)
        return self.render_to_response(self.get_context_data(form=form))

    def load_form(self, request):
        if self.form_class and (
                    self.__class__ == ContentCreateView or self.model == Item):
            form_kwargs = self.get_form_kwargs()
            form_kwargs.update({"request": request})
            form = self.form_class(**form_kwargs)
        else:
            form_class = self.get_form_class()
            form = self.get_form(form_class)
        return form

    def post(self, request, *args, **kwargs):
        form = self.load_form(request)
        if "next" in request.POST:
            self.success_url = request.POST.get("next")
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
            form.stores_search()
            return self.render_to_response(self.get_context_data(form=form))
        elif form.is_valid():
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


class ContentUpdateView(ContentView, ContentFormMixin, UpdateView):

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ContentUpdateView, self).dispatch(request,
                                                       *args,
                                                       **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        kwargs = {"form": form}
        if "next" in request.GET:
            kwargs.update({"next": request.GET.get("next")})
        return self.render_to_response(self.get_context_data(**kwargs))

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


class ContentDetailView(ContentView, DetailView, FormMixin, ProcessFollowView,
                                                            ProcessVoteView):

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
        if self.model == Item:
            item = context["item"]

            feats = Feature.objects.filter(
                        Q(items__id=item.id) & Q(status=Content.STATUS.public)
            )

            questions = Question.objects.filter(
                Q(items__id=item.id) & Q(status=Content.STATUS.public)
            )

            POST_dict = self.request.POST.copy()

            if "question" in POST_dict:
                q_form = QuestionForm(POST_dict, request=self.request)
            else:
                q_form = QuestionForm(request=self.request)

            if "answer" in POST_dict and "question_id" in POST_dict:
                for q in questions:
                    if q.id != int(POST_dict["question_id"]):
                        q.answer_form = AnswerForm(request=self.request)
                    else:
                        q.answer_form = AnswerForm(POST_dict,
                                                        request=self.request)
            else:
                for q in questions:
                    q.answer_form = AnswerForm(request=self.request)

            sets = {
                "questions": questions,
                "links": Link.objects.filter(
                    Q(items__id=item.id) & Q(status=Content.STATUS.public)
                ),
                "feat_pos": feats.filter(positive=True),
                "feat_neg": feats.filter(positive=False)
            }

            for k in sets.keys():
                sets.update({k: sorted(list(sets[k]), key=lambda c:
                    Vote.objects.get_score(c)['score'], reverse=True)
                })

            sets.update({"feat_lists": [sets["feat_pos"], sets["feat_neg"]]})
            del sets["feat_pos"]
            del sets["feat_neg"]
            context.update(sets)

            tag_ids = self.object.tags.values_list('id', flat=True)
            p_list = Profile.objects.filter(skills__id__in=tag_ids).distinct()
            context.update({"q_form": q_form, "prof_list": p_list})

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

            new_item = sync_products(Item, self.object)
            albums = new_item.successors.filter(data__contains={
                'class': 'image_set', 'name': 'main album'
            })
            if albums:
                # This is a way to order by values of an hstore key
                images = albums[0].successors.all().extra(
                    select={"order": "content_relation.data -> 'order'"},
                    order_by=['order', ]
                )
                context.update({'album': images})

        elif self.model == Question:
            question = context.pop("question")
            if "answer" in self.request.POST:
                question.answer_form = AnswerForm(self.request.POST,
                                                        request=self.request)
            else:
                question.answer_form = AnswerForm(request=self.request)

            tag_ids = question.items.all().values_list("tags__id", flat=True)
            p_list = Profile.objects.filter(skills__id__in=tag_ids).distinct()
            context.update({"question": question, "prof_list": p_list})

            item_list = question.items.all()
            queryset = Question.objects.filter(
                    items__id__in=item_list.values_list("id", flat=True))
            queryset = queryset.exclude(id=question.id)
            queryset_ordered = generic_annotate(
                    queryset, Vote, Sum('votes__vote')).order_by("-score")
            context.update({
                "item_list": item_list,
                "related_questions": {
                    _("Top related questions"): queryset_ordered[:3],
                    _("Latest related questions"): queryset[:3]
                }
            })

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
        self.object = form.save(**kwargs)
        form.save_m2m()
        messages.add_message(self.request,
            self.messages["object_created"]["level"],
            self.messages["object_created"]["text"] % {
                "user": user_display(self.request.user),
                "object": self.object._meta.verbose_name
            }
        )
        return HttpResponseRedirect(self.get_success_url())

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if "next" in request.POST:
            self.success_url = request.POST.get("next")
        if "ask" in request.POST:
            obj = load_object(request)
            if self.model == Item:
                item = self.get_object()
                success_url = obj.get_product_related_url(item)
            else:
                success_url = obj.get_absolute_url()
            return process_asking(request, obj, success_url)
        elif "question" in request.POST or "answer" in request.POST:
            if "question" in request.POST:
                POST_dict = request.POST.copy()
                POST_dict.update(
                    {'status': Content._meta.get_field('status').default}
                )
                form = QuestionForm(POST_dict, request=request)
            else:
                form = AnswerForm(request.POST, request=request)
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


class ProcessSearchView(RedirectView):

    def post(self, request, *args, **kwargs):
        if "item_search" in request.POST:
            search = request.POST.get("item_search")
            item_list = Item.objects.filter(name=search)
            tag_list = Tag.objects.filter(name=search)
            if item_list.count() == 1:
                response = item_list[0].get_absolute_url()
            elif tag_list.count() == 1:
                response = reverse("tagged_items", rgs=[tag_list[0].slug])
            else:
                response = "%s?search=%s" % (reverse("item_index"), search)
            return HttpResponseRedirect(response)
        return super(ProcessSearchView, self).post(request, *args, **kwargs)


class ContentListView(ContentView, ListView, ProcessSearchView):

    model = Item
    template_name = "items/item_list_image.html"
    paginate_by = 9

    def get_queryset(self):
        queryset = super(ContentListView, self).get_queryset()
        if "sort_products" in self.request.POST:
            self.sort_order = self.request.POST.get("sort_products")
        else:
            self.sort_order = "-pub_date"
        if self.sort_order == "popular":
            pass
            #FIXME Not working, don't know the hell why...
#                queryset = queryset.annotate(
#                                Count("content")).order_by("-content__count")
        else:
            queryset = queryset.order_by(self.sort_order)
        if "tag_slug" in self.kwargs:
            self.tag = Tag.objects.get(slug=self.kwargs["tag_slug"])
            queryset = queryset.filter(tags=self.tag)
        if "search" in self.request.GET:
            self.search_terms = self.request.GET.get("search", "")
            if self.search_terms:
                self.template_name = "items/item_list_text.html"
                query = get_query(self.search_terms, ["name"])
                queryset = queryset.filter(query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ContentListView, self).get_context_data(**kwargs)
        for attr in ["tag", "search_terms", "sort_order"]:
            context.update({attr: getattr(self, attr, "")})
        if "item_list" in context:
            item_list = context.get("item_list")
            if item_list.count() > 0:
                queryset = Question.objects.filter(
                        items__id__in=item_list.values_list("id", flat=True))
                queryset_ordered = generic_annotate(
                        queryset, Vote, Sum('votes__vote')).order_by("-score")
                context.update({
                    "media": ChosenSelect().media,
                    "item_list": item_list,
                    "related_questions": {
                        _("Top Questions"): queryset_ordered[:3],
                        _("Latest Questions"): queryset[:3]
                    }
                })
        return context


class ContentDeleteView(ContentView, DeleteView):

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not request.user.has_perm("can_manage", self.object):
            raise PermissionDenied
        success_url = self.get_success_url(request)
        self.object.delete()
        return HttpResponseRedirect(success_url)

    def get_success_url(self, request):
        if self.model.__name__ == "Item":
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
