from django.conf import settings
from django.db.models import Count
from django.views.generic import ListView
from django.views.generic.simple import direct_to_template

from items.models import Item, Content


class HomepageView(ListView):

    paginate_by = 14

    def get_context_data(self, **kwargs):
        context = super(HomepageView, self).get_context_data(**kwargs)

        if settings.DEBUG:
            temp_av_list = {
                "homepage_products.html" : {
                    "1" : "Template trial: doc",
                    "2" : "Template trial: empty"
                },
                "homepage_contents.html" : {
                    "1" : "Exemple !",
                }
            }

            names = super(HomepageView, self).get_template_names()

            if temp_av_list[names[0]]:
                temp_av = temp_av_list[names[0]]

                context.update({"temp_av": temp_av})

        return context

    def get_template_names(self):
        names = super(HomepageView, self).get_template_names()

        if "template_test" in self.request.GET:
            names[0] = names[0] + '_' + self.request.GET['template_test']

        return names

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
        elif kwargs.get("cat") == "newsfeed":
            self.queryset = Content.objects.all().select_subclasses()
            self.template_name = "homepage_contents.html"
        else:
            pass
        return super(HomepageView, self).get(request, *args, **kwargs)
        # else:
        #     return direct_to_template(request, "homepage.html")
