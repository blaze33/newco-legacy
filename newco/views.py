from django.db.models import Count
from django.views.generic import ListView
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from taggit.models import Tag
from items.models import Item, Question
from utils.multitemplate.views import MultiTemplateMixin

from datetime import datetime, timedelta

import json

class HomepageView(MultiTemplateMixin, ListView):

    paginate_by = 14

    def get(self, request, *args, **kwargs):
        self.cat = kwargs.get("cat", "home")
        if self.cat == "home" or self.cat == "last":
            self.queryset = Item.objects.all()
            self.template_name = "homepage_products.html"
            if self.cat == "home":
                week_ago = datetime.now() - timedelta(days=7)
                self.queryset = self.queryset.filter(content__pub_date__gt=week_ago)
                self.queryset = self.queryset.annotate(
                    Count("content")).order_by("-content__count")
            else:
                self.queryset = self.queryset.order_by("-pub_date")
        elif self.cat == "questions":
            self.queryset = Question.objects.annotate(
                score=Count("answer")).filter(score__lte=0)
            if "cat" in self.request.GET:
                self.search_terms = self.request.GET.get("cat", "")
                category=self.search_terms
                print category
                self.queryset=self.queryset.filter(tags__name__contains=category)
                if self.search_terms:
                    self.template_name = "homepage_questions.html"
            else:
                self.template_name = "homepage_questions.html"   
        else:
            pass
        return super(HomepageView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs.update({"cat": self.cat})
        tag_names=json.dumps(list(Tag.objects.all().values_list("name", flat=True)))
        kwargs.update({"data_source_tags":tag_names,})
        if "cat" in self.request.GET:
            self.search_terms = self.request.GET.get("cat", "")
            category=self.search_terms
            kwargs.update({"category":category,})
        return super(HomepageView, self).get_context_data(**kwargs)
    
    def post(self, request, *args, **kwargs):
        if "select_category_tag" in request.POST:
            category = request.POST.get("select_category_tag")
            response = "%s?cat=%s" % (reverse("home", kwargs={"cat":"questions"}), category)
            return HttpResponseRedirect(response)
        return super(HomepageView, self).post(request, *args, **kwargs)
