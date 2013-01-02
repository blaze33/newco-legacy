from django.core.urlresolvers import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from follow.models import Follow

from items.models import Content, Item
from profiles.models import Profile
from utils.follow.views import FollowMixin
from utils.vote.views import VoteMixin

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
        "empty_msg": mark_safe(_("You don't follow anything nor anyone yet. "
                                 "Find people or products to follow on your "
                                 "right, or navigating NewCo!")),
        "page_url": reverse_lazy("dash", args=["feed"]),
    },
    "contribution": {
        "title": _("Contribution center"),
        "subtitle": mark_safe(_("Latest activity on your skills tags."
                                " Maybe you would like to contribute?")),
        "name": "contrib",
        "mini_feed": "True",
        "page_url": reverse_lazy("dash", args=["contribution"]),
    },
    "draft": {
        "title": _("Drafts"),
        "subtitle": mark_safe(_("Complete and publish some?")),
        "name": "drafts",
        "mini_feed": "True",
        "empty_msg": _("You don't have any drafts."),
        "page_url": reverse_lazy("dash", args=["draft"]),
    },
    "all": {
        "title": _("All my contributions"),
        "subtitle": _("Your latest contributions"),
        "name": "all",
        "mini_feed": "True",
        "page_url": reverse_lazy("dash", args=["all"]),
    },
}

WHAT_TO_FOLLOW_PARAMS = {
    "users": {"class": User, "fieldname": "target_user_id", "nb_obj": 2},
    "items": {"class": Item, "fieldname": "target_item_id", "nb_obj": 1},
}


class DashboardView(ListView, FollowMixin, VoteMixin):

    queryset = Content.objects.all().prefetch_related(
        "author__reputation", "items")

    def __init__(self, **kwargs):
        super(DashboardView, self).__init__(**kwargs)
        BOXES.get("contribution").update({"empty_msg": mark_safe(_(
            "We don't know what to advice you to contribute on, we would need "
            "to know more about you. Maybe you could <a href='%(url_ed)s'>"
            "add skill tags</a> to your profile?") % {
                "url_ed": reverse_lazy("profile_edit")})
        })
        BOXES.get("all").update({"empty_msg": mark_safe(_(
            "You haven't contributed yet. Have you checked the "
            "<a href='%(url_cont)s'>"
            "How to contribute</a> page?") % {
                "url_cont": reverse_lazy("contribute")})
        })

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
                self.queryset = self.queryset.get_feed(self.user)
            elif self.page == "contribution":
                self.queryset = self.queryset.get_related_contributions(
                    self.user, Item.objects.all()).exclude(author=self.user)
#            elif self.page == "collaboration":
            elif self.page == "draft" or self.page == "all":
                self.queryset = self.queryset.filter(author=self.user)
                if self.page == "draft":
                    self.queryset = self.queryset.draft()
#            elif self.page == "shopping":
#            elif self.page == "purchase":
            self.scores = self.queryset.get_scores()
        self.queryset = self.queryset.prefetch_related(
            "author__reputation", "items")
        self.queryset = self.queryset.select_subclasses()
        self.page_name = PAGES_TITLES.get(self.page)
        return super(DashboardView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)

        if self.page == "dashboard":
            feed = self.queryset.get_feed(self.user).prefetch_related(
                "author__reputation", "items")
            all_my_contrib = self.queryset.filter(
                author=self.user).prefetch_related(
                    "author__reputation", "items")
            drafts = all_my_contrib.draft().prefetch_related(
                "author__reputation", "items")
            contrib_feed = self.queryset.get_related_contributions(
                self.user, Item.objects.all()).exclude(
                    author=self.user).prefetch_related(
                        "author__reputation", "items")

            boxes = BOXES
            boxes.get("feed").update({"feed": feed.select_subclasses()[:4]})
            boxes.get("contribution").update(
                {"feed": contrib_feed.select_subclasses()[:4]})
            boxes.get("draft").update(
                {"feed": drafts.select_subclasses()[:4]})
            boxes.get("all").update(
                {"feed": all_my_contrib.select_subclasses()[:4]})
            context.update({"boxes": boxes})
        else:
            empty_msg = BOXES.get(self.page).get("empty_msg")
            context.update({"empty_msg": empty_msg, "object_list":
                            context["object_list"].prefetch_items_image(Item)})
            if self.page == "feed":
                # "Who to follow": For now, random on not followed people/items
                objects_followed = Follow.objects.filter(user=self.user)
                wtf = {}
                for key, value in WHAT_TO_FOLLOW_PARAMS.items():
                    ids = filter(None, objects_followed.values_list(
                        value.get("fieldname"), flat=True))
                    non_fwed = value.get("class").objects.exclude(id__in=ids)
                    nb_obj = value.get("nb_obj")
                    wtf.update({key: non_fwed.order_by("?")[:nb_obj]})
                context.update({"wtf": wtf})

        context.update({
            "my_profile": Profile.objects.get(user=self.user),
            "data_source_profile": Profile.objects.get_all_names(),
            "page": self.page,
            "page_name": self.page_name,
            "scores": getattr(self, "scores", {}),
            "votes": getattr(self, "votes", {})
        })
        return context
