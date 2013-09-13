import datetime

from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView
from django.views.generic.edit import FormMixin

from items.models import Item, Content, TopCategories
from utils.help.views import AskForHelpMixin
from utils.multitemplate.views import MultiTemplateMixin
from utils.views.tutorial import TutorialMixin
from utils.vote.views import VoteMixin

DEFAULT_CATGORY = "products"
DEFAULT_FILTERS = {"products": "popular", "questions": "unanswered"}


class CategoryMixin(object):

    def get(self, request, *args, **kwargs):
        self.cat = kwargs.get("cat", DEFAULT_CATGORY)
        self.filter = kwargs.get("filter", DEFAULT_FILTERS.get(self.cat))
        self.groups = request.GET.get("communities", "").split(",")
        self.template_name = "homepage_{0}.html".format(self.cat)
        delta = timezone.now() - datetime.timedelta(days=20 * 31)
        if self.cat == "products":
            self.model = Item
            self.queryset = Item.objects.all()
            if self.groups:
                self.queryset = self.queryset.filter(
                    tags__name__in=self.groups)
            if self.filter == "popular":
                self.queryset = self.queryset.filter(
                    content__created__gt=delta)
            self.queryset = self.queryset.order_queryset(self.filter)
        elif self.cat == "questions":
            self.queryset = Content.objects.questions()
            if self.groups != [""]:
                item_qs = Item.objects.filter(tags__name__in=self.groups)
                self.queryset = self.queryset.filter(
                    Q(items__in=item_qs) | Q(tags__name__in=self.groups)
                ).distinct()
            if self.filter == "popular":
                self.queryset = self.queryset.filter(created__gt=delta)
            self.scores, self.votes = self.queryset.get_scores_and_votes(
                request.user)
            self.queryset = self.queryset.order_queryset(self.filter,
                                                         self.scores)
            self.empty_msg = mark_safe(_(
                "There is no question in this category. "
                "<a class='btn' href='{create_url}'>Ask your own!</a>").format(
                    create_url=reverse_lazy("item_create", args=["question"])))

        return super(CategoryMixin, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        if "communities" in self.request.GET:
            kwargs.update({
                "communities": self.groups,
                "communities_query": "?communities=" + ",".join(self.groups)})
        return super(CategoryMixin, self).get_context_data(**kwargs)


class TopCommunitiesMixin(object):

    top_groups = TopCategories()

    def get_context_data(self, **kwargs):
        kwargs.update({
            "top_communities": self.top_groups.sub_categories()[:8]})
        if "choose_community" in self.kwargs and \
                "communities" not in self.request.GET:
            self.template_name = "homepage_communities.html"
            kwargs["top_products"] = self.top_groups.top_products_by_categories(
                kwargs["top_communities"])
        return super(TopCommunitiesMixin, self).get_context_data(**kwargs)


class HomepageView(TopCommunitiesMixin,
                   CategoryMixin, MultiTemplateMixin, TutorialMixin,
                   AskForHelpMixin, ListView, FormMixin, VoteMixin):

    paginate_by = 14

    def get_context_data(self, **kwargs):
        for attr in ["cat", "filter", "scores", "votes", "empty_msg"]:
            if hasattr(self, attr):
                kwargs.update({attr: getattr(self, attr)})
        ctx = super(HomepageView, self).get_context_data(**kwargs)
        if self.model == Item:
            ctx.get("object_list").fetch_images()
        return ctx
