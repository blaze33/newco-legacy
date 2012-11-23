import datetime

from django.db.models import Count
from django.utils import timezone
from django.views.generic import ListView

from items.models import Item, Question
from utils.multitemplate.views import MultiTemplateMixin
from utils.tutorial.views import TutoMixin

class HomepageView(MultiTemplateMixin, TutoMixin, ListView):

    paginate_by = 14

    def get(self, request, *args, **kwargs):
        self.cat = kwargs.get("cat", "home")
        if self.cat == "home" or self.cat == "last":
            self.model = Item
            self.queryset = Item.objects.all()
            self.template_name = "homepage_products.html"
            if self.cat == "home":
                delta = timezone.now() - datetime.timedelta(days=30)
                self.queryset = self.queryset.filter(
                    content__pub_date__gt=delta)
                self.queryset = self.queryset.annotate(
                    Count("content")).order_by("-content__count")
            else:
                self.queryset = self.queryset.order_by("-pub_date")
        elif self.cat == "questions":
            self.queryset = Question.objects.annotate(
                score=Count("answer")).filter(score__lte=0)
            self.template_name = "homepage_contents.html"
        else:
            pass
        return super(HomepageView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs.update({"cat": self.cat})
        ctx = super(HomepageView, self).get_context_data(**kwargs)
        if self.model == Item:
            ctx.get("object_list").fetch_images()
        return ctx
