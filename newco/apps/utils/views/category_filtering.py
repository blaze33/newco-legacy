
### GK Add for categories filtering ###
import datetime

from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.views.generic import ListView
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404


from items.models import Item, Content
from taggit.models import Tag


DEFAULT_CATGORY = "products"
DEFAULT_FILTERS = {"products": "popular", "questions": "unanswered"}
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
                category=self.search_terms
                try:
                    self.tag = get_object_or_404(Tag, slug=category)
                    item_ids = Item.objects.filter(tags=self.tag).values_list(
                        "id", flat=True)
                    if self.filter == "popular":
                        self.queryset = Content.objects.questions()
                        self.queryset = self.queryset.filter(pub_date__gt=delta)
                        self.queryset = self.queryset.filter(Q(items__in=item_ids)|Q(tags__name__contains=category))
                        self.queryset = self.queryset.order_queryset(self.filter)
                    else:
                        self.queryset = self.queryset.filter(Q(items__in=item_ids)|Q(tags__name__contains=category))
                except:
                    return super(CategoryMixin, self).get(request, *args, **kwargs)
        return super(CategoryMixin, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        if "category" in self.request.GET:
            self.search_terms = self.request.GET.get("category", "")
            category_name=self.search_terms
            kwargs.update({"category_name":category_name,})
        return super(CategoryMixin, self).get_context_data(**kwargs)
    
    def post(self, request, *args, **kwargs):
        if "select_category" in request.POST:
            self.filter = kwargs.get("filter", DEFAULT_FILTERS.get("questions"))
            select_category = request.POST["select_category"]
            response = "%s?category=%s" % (reverse("home", kwargs={"cat":"questions", "filter":self.filter}), select_category)
            return HttpResponseRedirect(response)
        elif "sort_products" in request.POST:
            self.sort_order = self.request.POST.get("sort_products")
            return self.get(request, *args, **kwargs)
        return super(CategoryMixin, self).post(request, *args, **kwargs)
