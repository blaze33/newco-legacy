from django.db.models import Count
from django.views.generic import ListView

from items.models import Item, Question


class HomepageView(ListView):

    paginate_by = 14

    def get(self, request, *args, **kwargs):
        self.cat = kwargs.get("cat", "home")
        if self.cat == "home" or self.cat == "last":
            self.queryset = Item.objects.all()
            self.template_name = "homepage_products.html"
            if self.cat == "home":
                self.queryset = self.queryset.annotate(
                    Count("content")).order_by("-content__count")
            else:
                self.queryset = self.queryset.order_by("-pub_date")
        elif self.cat == "questions":
            self.queryset = Question.objects.annotate(
                score=Count("answer")).filter(score__lte=0)
            self.template_name = "homepage_questions.html"
        else:
            pass
        return super(HomepageView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs.update({"cat": self.cat})
        return super(HomepageView, self).get_context_data(**kwargs)
