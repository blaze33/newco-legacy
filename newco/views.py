import datetime

from django.db.models import Count
from django.utils import timezone
from django.views.generic import ListView
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from items.models import Item, Question
from utils.multitemplate.views import MultiTemplateMixin


class HomepageView(MultiTemplateMixin, ListView):

    paginate_by = 14
    sort_order = "popular"

    def get(self, request, *args, **kwargs):
        self.cat = kwargs.get("cat", "home")
        if self.cat == "home":
            self.model = Item
            self.queryset = Item.objects.all()
            self.template_name = "homepage_products.html"
            if self.sort_order == "popular":
                delta = timezone.now() - datetime.timedelta(days=30)
                self.queryset = self.queryset.filter(
                    content__pub_date__gt=delta)
                self.queryset = self.queryset.annotate(
                    Count("content")).order_by("-content__count")
            elif self.sort_order == "last":
                self.queryset = self.queryset.order_by("-pub_date")
        elif self.cat == "questions":
            self.model = Question
            self.queryset = Question.objects.annotate(
                score=Count("answer")).filter(score__lte=0)
            if "category" in self.request.GET:
                self.search_terms = self.request.GET.get("category", "")
                category=self.search_terms
                self.queryset=self.queryset.filter(tags__name__contains=category)
                if self.search_terms:
                    self.template_name = "homepage_questions.html"
            self.template_name = "homepage_questions.html"
        else:
            pass
        return super(HomepageView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs.update({"cat": self.cat, "sort_order":self.sort_order})
        ctx = super(HomepageView, self).get_context_data(**kwargs)
        if self.model == Item:
            ctx.get("object_list").fetch_images()
            return ctx
        if self.model == Question:
            question_qs = Question.objects.all().values('items')
            item_qs = Item.objects.filter(id__in=question_qs.values_list("items", flat=True))
            item_qs.fetch_images()
        if "category" in self.request.GET:
            self.search_terms = self.request.GET.get("category", "")
            category_name=self.search_terms
            kwargs.update({"category_name":category_name,})
        return super(HomepageView, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        if "select_category" in request.POST:
            select_category = request.POST["select_category"]
            response = "%s?category=%s" % (reverse("home", kwargs={"cat":"questions"}), select_category)
            return HttpResponseRedirect(response)
        elif "sort_products" in request.POST:
            self.sort_order = self.request.POST.get("sort_products")
            return self.get(request, *args, **kwargs)
        return super(HomepageView, self).post(request, *args, **kwargs)
