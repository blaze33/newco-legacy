from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from follow.models import Follow
from voting.models import Vote

from items.models import Content, Item
from profiles.models import Profile
from profiles.views import ProcessProfileSearchView
from utils.follow.views import ProcessFollowView

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

WHAT_TO_FOLLOW_PARAMS = {
    "users": {"class": User, "fieldname": "target_user_id", "nb_obj": 2},
    "items": {"class": Item, "fieldname": "target_item_id", "nb_obj": 1},
}


class DashboardView(ListView, ProcessProfileSearchView, ProcessFollowView):

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
            self.scores = Vote.objects.get_scores_in_bulk(self.queryset)
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
            wtf = dict()
            for key, value in WHAT_TO_FOLLOW_PARAMS.items():
                ids = filter(None, objects_followed.values_list(
                                            value.get("fieldname"), flat=True))
                non_fwed = value.get("class").objects.exclude(id__in=ids)
                wtf.update({key: non_fwed.order_by("?")[:value.get("nb_obj")]})
            context.update({"wtf": wtf})

        context.update({
            "my_profile": Profile.objects.get(user=self.user),
            "data_source_profile": Profile.objects.get_all_names(),
            "page": self.page,
            "page_name": self.page_name,
            "scores": getattr(self, "scores", {})
        })
        return context
