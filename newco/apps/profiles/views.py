from django.http import HttpResponsePermanentRedirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic.list import MultipleObjectMixin

from django.contrib.auth.models import User

from account.utils import user_display
from follow.models import Follow
from idios.views import ProfileDetailView, ProfileListView

from items.models import Item
from utils.follow.views import FollowMixin
from utils.views import TutorialMixin


class ProfileDetailView(TutorialMixin, ProfileDetailView, MultipleObjectMixin,
                        FollowMixin):

    paginate_by = 10

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.slug and kwargs["slug"] != self.object.slug:
            url = self.object.get_absolute_url()
            return HttpResponsePermanentRedirect(url)
        return super(ProfileDetailView, self).get(request, *args, **kwargs)

    def get_object(self):
        if hasattr(self, "object"):
            return self.object
        return super(ProfileDetailView, self).get_object()

    def get_context_data(self, **kwargs):
        history = self.page_user.content_set.public().prefetch_related(
            "author__reputation", "items")
        fwers_ids = Follow.objects.get_follows(
            self.page_user).values_list("user_id", flat=True)
        obj_fwed = Follow.objects.filter(user=self.page_user)
        fwees_ids = obj_fwed.values_list("target_user_id", flat=True)
        items_fwed_ids = obj_fwed.values_list("target_item_id", flat=True)

        empty_msg = _("%(page_user_display)s have not contributed yet.") % {
            "page_user_display": user_display(self.page_user)
        }

        context = super(ProfileDetailView, self).get_context_data(**kwargs)
        followers = User.objects.filter(pk__in=fwers_ids)
        followees = User.objects.filter(pk__in=fwees_ids)
        context.update({
            "empty_msg": empty_msg,
            "reputation": self.page_user.reputation,
            "fwers": followers.order_by("-reputation__reputation_incremented"),
            "fwees": followees.order_by("-reputation__reputation_incremented"),
            "items_fwed": Item.objects.filter(pk__in=items_fwed_ids),
            "scores": history.get_scores(),
        })

        # Next step would be to be able to "merge" the get_context_data of both
        # DetailView (SingleObjectMixin) and MultipleObjectMixin
        m = MultipleObjectMixin()
        m.request = self.request
        m.kwargs = self.kwargs
        m.paginate_by = self.paginate_by

        history = history.select_subclasses()
        context.update(m.get_context_data(object_list=history))

        return context


class ProfileListView(TutorialMixin, ProfileListView):

    paginate_by = 15
    template_name = "profiles/profiles.html"

    def get_queryset(self):
        profiles = self.get_model_class().objects.all().prefetch_related(
            "user__reputation")

        search_terms = self.request.GET.get("search", "")
        order = self.request.GET.get("order", "")

        if search_terms:
            profiles = profiles.filter(name__icontains=search_terms)
        if order == "date":
            profiles = profiles.order_by("-user__date_joined")
        elif order == "name":
            profiles = profiles.order_by("name")
        else:
            profiles = profiles.order_by(
                "-user__reputation__reputation_incremented", "name")

        return profiles
