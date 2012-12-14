import datetime

from django.db.models import Count, Sum
from django.utils import timezone
from django.views.generic import ListView

from items.models import Item, Content
from utils.multitemplate.views import MultiTemplateMixin
from utils.views.tutorial import TutorialMixin
from utils.views.category_filtering import CategoryMixin
from newco import DEFAULT_FILTERS, DEFAULT_CATGORY


class HomepageView(CategoryMixin, MultiTemplateMixin, TutorialMixin, ListView):

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
            self.queryset = self.queryset.order_queryset(self.filter)

        return super(HomepageView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs.update({"cat": self.cat, "filter": self.filter})
        ctx = super(HomepageView, self).get_context_data(**kwargs)
        if self.model == Item:
            ctx.get("object_list").fetch_images()
        return ctx
 