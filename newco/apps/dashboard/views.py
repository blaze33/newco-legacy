from django.views.generic import ListView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _

from django.db.models import Q
from django.core.urlresolvers import reverse_lazy

from django.contrib.auth.decorators import login_required

from items.models import Content, Item
from profiles.models import Profile
from profiles.views import ProcessProfileSearchView
from utils.followtools import process_following
from utils.tools import load_object
from follow.models import Follow

PAGES_TITLES = {
    "dashboard": _("Dashboard"),
    "feed": _("Feed"),
    "contribution": _("Contribution center"),
    "collaboration": _("Teamwork"),
    "draft": _("Drafts"),
    "all": _("All my contributions"),
    "shopping": _("Shopping notes"),
    "purchase": _("Purchase history"),
}

BOXES = {
    "feed": {
        "title": _("My newsfeed"),
        "subtitle": _("Mini feed from what you follow"),
        "name": "feed",
        "mini_feed": "True",
        "page_url": reverse_lazy("dash", args=["feed"]),
    },
    "contrib": {
        "title": _("Contribution center"),
        "subtitle": _("Latest activity on your skills tags..."
                        " Maybe you would like to contribute?"),
        "name": "contrib",
        "mini_feed": "True",
        "page_url": reverse_lazy("dash", args=["contribution"]),
    },
    "drafts": {
        "title": _("Drafts"),
        "subtitle": _("Maybe you want to complete and publish some?"),
        "name": "drafts",
        "mini_feed": "True",
        "page_url": reverse_lazy("dash", args=["draft"]),
    },
    "all_my_contrib": {
        "title": _("All my contributions"),
        "subtitle": _("Your latest contributions"),
        "name": "all_my_contrib",
        "mini_feed": "True",
        "page_url": reverse_lazy("dash", args=["all"]),
    },
}


class DashboardView(ListView, ProcessProfileSearchView):

    queryset = Content.objects.all()

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(DashboardView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.user = request.user
        if not "cat" in kwargs:
            self.template_name = "dashboard/home.html"
            self.page = "dashboard"
        else:
            self.page = kwargs.get("cat")
            self.template_name = "dashboard/" + self.page + ".html"
            self.paginate_by = 14
            if self.page == "feed":
                self.queryset = Content.objects.get_feed(self.user)
            elif self.page == "contribution":
                self.queryset = Content.objects.get_related_contributions(
                                                                    self.user)
#            elif self.page == "collaboration":
            elif self.page == "draft" or self.page == "all":
                self.queryset = self.queryset.filter(author=self.user)
                if self.page == "draft":
                    self.queryset = self.queryset.filter(
                                                status=Content.STATUS.draft)
#            elif self.page == "shopping":
#            elif self.page == "purchase":
        self.queryset = self.queryset.select_subclasses()
        self.page_name = PAGES_TITLES.get(self.page)
        return super(DashboardView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)

        if self.page == "dashboard":
            drafts = Content.objects.filter(
                Q(author=self.user) & Q(status=Content.STATUS.draft)
            )
            feed = Content.objects.get_feed(self.user)
            all_my_contrib = Content.objects.filter(author=self.user)
            contrib_feed = Content.objects.get_related_contributions(self.user)

            boxes = BOXES
            boxes.get("feed").update({"feed": feed.select_subclasses()[:4]})
            boxes.get("contrib").update(
                            {"feed": contrib_feed.select_subclasses()[:4]})
            boxes.get("drafts").update(
                            {"feed": drafts.select_subclasses()[:4]})
            boxes.get("all_my_contrib").update(
                            {"feed": all_my_contrib.select_subclasses()[:4]})
            context.update({"boxes": boxes})
        elif self.page == "feed":
            #"Who to follow" List. For now, random on not followed people/items
            objects_followed = Follow.objects.filter(user=self.user)
            user_ids = filter(None, objects_followed.values_list(
                                                "target_user_id", flat=True))
            item_ids = filter(None, objects_followed.values_list(
                                                "target_item_id", flat=True))
            non_fwed_profiles = Profile.objects.exclude(user_id__in=user_ids)
            non_fwed_items = Item.objects.exclude(id__in=item_ids)
            wtf = {
                "profiles": non_fwed_profiles.order_by("?")[:2],
                "items": non_fwed_items.order_by("?")[:1]
            }
            context.update({"wtf": wtf})

        context.update({
            "my_profile": Profile.objects.get(user=self.user),
            "data_source_profile": Profile.objects.get_all_names(),
            "page": self.page,
            "page_name": self.page_name,
        })
        return context

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        if "follow" in request.POST or "unfollow" in request.POST:
            obj_followed = load_object(request)
            success_url = obj_followed.get_absolute_url()
            return process_following(request, obj_followed, success_url)
