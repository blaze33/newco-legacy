import datetime

from django.core.urlresolvers import reverse_lazy
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView
from django.views.generic.edit import FormMixin

from items.models import Item, Content
from items.views import TopCategoriesView
from utils.help.views import AskForHelpMixin
from utils.multitemplate.views import MultiTemplateMixin
from utils.views.tutorial import TutorialMixin
from utils.vote.views import VoteMixin

DEFAULT_CATGORY = "products"
DEFAULT_FILTERS = {"products": "popular", "questions": "unanswered"}

# CategoryMixin imports
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect


class CategoryMixin(object):

    def get(self, request, *args, **kwargs):
        self.cat = kwargs.get("cat", DEFAULT_CATGORY)
        self.filter = kwargs.get("filter", DEFAULT_FILTERS.get(self.cat))
        self.groups = request.GET.get('communities', '').split(',')
        self.template_name = "homepage_products.html"
        delta = timezone.now() - datetime.timedelta(days=4*31)
        if self.cat == "products":
            self.model = Item
            self.queryset = Item.objects.all()
            if self.groups:
                self.queryset = self.queryset.filter(tags__name__in=self.groups)
            if self.filter == "popular":
                self.queryset = self.queryset.filter(
                    content__created__gt=delta)
            self.queryset = self.queryset.order_queryset(self.filter)
        elif self.cat == "questions":
            self.template_name = "homepage_questions.html"
            self.queryset = Content.objects.questions()
            if self.groups != ['']:
                item_ids = Item.objects.filter(tags__name__in=self.groups).values_list("id", flat=True)
                self.queryset = self.queryset.filter(
                    Q(items__in=item_ids) | Q(tags__name__in=self.groups)).distinct()
            if self.filter == "popular":
                self.queryset = self.queryset.filter(created__gt=delta)
            self.scores, self.votes = self.queryset.get_scores_and_votes(
                request.user)
            self.queryset = self.queryset.order_queryset(self.filter)
            self.empty_msg = mark_safe(_(
                "There is no question in this category. "
                "<a class='btn' href='{create_url}'>Ask your own!</a>").format(
                    create_url=reverse_lazy("item_create", args=["question"])))

        return super(CategoryMixin, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        if "category" in self.request.GET:
            self.search_terms = self.request.GET.get("category", "")
            category_name = self.search_terms
            kwargs.update({"category_name": category_name})
        if "communities" in self.request.GET:
            kwargs.update({"communities": self.groups})
            kwargs.update({'communities_query': '?communities=' + ','.join(self.groups)})
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


class TopCommunitiesMixin(object):

    def top_products_by_categories(self, category):
        delta = timezone.now() - datetime.timedelta(days=4*31)
        return Item.objects.filter(tags__name__in=[unicode(category)],
                content__created__gt=delta).order_queryset(
                "popular")[:6].fetch_images()

    def get_context_data(self, **kwargs):
        kwargs.update({"top_communities": TopCategoriesView().api_context_data()})
        if "communities" not in self.request.GET:
            self.template_name = "homepage_communities.html"
            kwargs['top_products'] = {}
            for cat in kwargs['top_communities']['object_list']:
                kwargs['top_products'].update({cat: self.top_products_by_categories(cat)})
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
