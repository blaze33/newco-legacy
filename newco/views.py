import datetime

from django.core.urlresolvers import reverse_lazy
from django.db.models import Count, Sum
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView
from django.views.generic.edit import FormMixin

from items.models import Item, Content
from utils.help.views import AskForHelpMixin
from utils.multitemplate.views import MultiTemplateMixin
from utils.views.tutorial import TutorialMixin
from utils.voting.views import VoteMixin

DEFAULT_CATGORY = "products"
DEFAULT_FILTERS = {"products": "popular", "questions": "unanswered"}

# CategoryMixin imports
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from taggit.models import Tag


class CategoryMixin(object):

    def get(self, request, *args, **kwargs):
        self.cat = kwargs.get("cat", DEFAULT_CATGORY)
        self.filter = kwargs.get("filter", DEFAULT_FILTERS.get(self.cat))
        delta = timezone.now() - datetime.timedelta(days=61)
        if self.cat == "questions":
            self.template_name = "homepage_questions.html"
            self.queryset = Content.objects.questions()
            if self.filter == "popular":
                self.queryset = self.queryset.filter(pub_date__gt=delta)
            self.queryset = self.queryset.order_queryset(self.filter)
            if "category" in self.request.GET:
                self.search_terms = self.request.GET.get("category", "")
                category = self.search_terms
                try:
                    self.tag = get_object_or_404(Tag, slug=category)
                    item_ids = Item.objects.filter(tags=self.tag).values_list(
                        "id", flat=True)
                    if self.filter == "popular":
                        self.queryset = Content.objects.questions()
                        self.queryset = self.queryset.filter(pub_date__gt=delta)
                        self.queryset = self.queryset.filter(Q(items__in=item_ids) | Q(tags__name__contains=category))
                        self.queryset = self.queryset.order_queryset(self.filter)
                    else:
                        self.queryset = self.queryset.filter(Q(items__in=item_ids) | Q(tags__name__contains=category))
                except:
                    return super(CategoryMixin, self).get(request, *args, **kwargs)
        return super(CategoryMixin, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        if "category" in self.request.GET:
            self.search_terms = self.request.GET.get("category", "")
            category_name = self.search_terms
            kwargs.update({"category_name": category_name})
        return super(CategoryMixin, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        if "select_category" in request.POST:
            self.filter = kwargs.get("filter", DEFAULT_FILTERS.get("questions"))
            select_category = request.POST["select_category"]
            response = "%s?category=%s" % (reverse("home", kwargs={"cat": "questions", "filter": self.filter}), select_category)
            return HttpResponseRedirect(response)
        elif "sort_products" in request.POST:
            self.sort_order = self.request.POST.get("sort_products")
            return self.get(request, *args, **kwargs)
        return super(CategoryMixin, self).post(request, *args, **kwargs)


class HomepageView(CategoryMixin, MultiTemplateMixin, TutorialMixin,
                   AskForHelpMixin, ListView, FormMixin, VoteMixin):

    paginate_by = 14

    def get(self, request, *args, **kwargs):
        self.cat = kwargs.get("cat", DEFAULT_CATGORY)
        self.filter = kwargs.get("filter", DEFAULT_FILTERS.get(self.cat))
        delta = timezone.now() - datetime.timedelta(days=61)
        if self.cat == "products":
            self.model = Item
            self.queryset = Item.objects.all()
            self.template_name = "homepage_products.html"
            if self.filter == "popular":
                self.queryset = self.queryset.filter(
                    content__pub_date__gt=delta).annotate(
                        count=Count("content__votes__vote"),
                        score=Sum("content__votes__vote")
                    ).filter(count__gt=0).order_by("-score")
            elif self.filter == "last":
                self.queryset = self.queryset.order_by("-pub_date")
        elif self.cat == "questions":
            self.template_name = "homepage_questions.html"
            self.queryset = Content.objects.questions()
            if self.filter == "popular":
                self.queryset = self.queryset.filter(pub_date__gt=delta)
            self.scores, self.votes = self.queryset.get_scores_and_votes(
                request.user)
            self.queryset = self.queryset.order_queryset(self.filter)
            self.empty_msg = mark_safe(_(
                "There is no question in this category. "
                "<a class='btn' href='{create_url}'>Ask your own!</a>").format(
                    create_url=reverse_lazy("item_create", args=["question"])))

        return super(HomepageView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        for attr in ["cat", "filter", "scores", "votes", "empty_msg"]:
            if hasattr(self, attr):
                kwargs.update({attr: getattr(self, attr)})
        ctx = super(HomepageView, self).get_context_data(**kwargs)
        if self.model == Item:
            ctx.get("object_list").fetch_images()
        return ctx
