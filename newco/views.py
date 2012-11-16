import datetime

from django.db.models import Count, Sum
from django.utils import timezone
from django.views.generic import ListView
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from items.models import Item, Question
from utils.multitemplate.views import MultiTemplateMixin


class HomepageView(MultiTemplateMixin, ListView):

    paginate_by = 14
    sort_p_order = "popular"
    sort_q_order = "unanswered"

    def get(self, request, *args, **kwargs):
        self.cat = kwargs.get("cat", "home")
        if self.cat == "home":
            self.model = Item
            self.queryset = Item.objects.all()
            self.template_name = "homepage_products.html"
            
        #### the variable "sort_p_order" can be changed from "popular"(by default) to "last" with buttons on template homepage_products_3 #####
            if self.sort_p_order == "popular":
                delta = timezone.now() - datetime.timedelta(days=30)
                self.queryset = self.queryset.filter(
                    content__pub_date__gt=delta)
                self.queryset = self.queryset.annotate(
                    count=Count("content__votes__vote"),
                    score=Sum("content__votes__vote")
                ).filter(count__gt=0).order_by("-score")
            elif self.sort_p_order == "last":
                self.queryset = self.queryset.order_by("-pub_date")
        if self.cat == "last":
            self.model = Item
            self.queryset = Item.objects.all()
            self.template_name = "homepage_products.html"
            self.queryset = self.queryset.order_by("-pub_date")
        elif self.cat == "questions":
            self.model = Question
            
        #### the variable "sort_q_order" can be changed from "unanswered"(by default) to "last_answered" with buttons on template homepage_questions_2 #####
            if self.sort_q_order == "unanswered":
                self.queryset = Question.objects.annotate(
                    score=Count("answer")).filter(score__lte=0)
            elif self.sort_q_order == "last_answered":
                self.queryset = Question.objects.annotate(
                    score=Count("answer")).filter(score__gt=0)
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
        kwargs.update({"cat": self.cat, "sort_p_order":self.sort_p_order, "sort_q_order":self.sort_q_order})
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
        ##### From homepage_products_3.html #####
        elif "sort_products" in request.POST:
            self.sort_p_order = self.request.POST.get("sort_products")
            return self.get(request, *args, **kwargs)
        ##### From homepage_questions_2.html -> questions.subnav.html #####
        elif "sort_questions" in request.POST:
            self.sort_q_order = self.request.POST.get("sort_questions")
            return self.get(request, *args, **kwargs)
        return super(HomepageView, self).post(request, *args, **kwargs)
