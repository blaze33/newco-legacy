from django.db.models import Count
from django.views.generic import ListView

from items.models import Item, Question


class HomepageView(ListView):

    paginate_by = 14

    def get(self, request, *args, **kwargs):
        # if request.user.is_authenticated() or "/content" in request.path:
        if not "cat" in kwargs or kwargs.get("cat") == "popular" or \
                kwargs.get("cat") == "last":
            self.queryset = Item.objects.all()
            self.template_name = "homepage_products.html"
            if kwargs.get("cat") == "last":
                self.queryset = self.queryset.order_by("-pub_date")
            else:
                self.queryset = self.queryset.annotate(
                    Count("content")).order_by("-content__count")
        elif kwargs.get("cat") == "questions":
            self.queryset = Question.objects.annotate(
                score=Count("answer")).filter(score__lte=0)
            self.template_name = "homepage_contents.html"
        else:
            pass
        return super(HomepageView, self).get(request, *args, **kwargs)
