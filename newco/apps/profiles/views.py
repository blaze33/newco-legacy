from django.db.models import Q
from django.http import HttpResponsePermanentRedirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic.list import MultipleObjectMixin

from django.contrib.auth.models import User

from account.utils import user_display
from follow.models import Follow
from idios.views import ProfileDetailView, ProfileListView
from voting.models import Vote

from items.models import Item, Content
from profiles.models import Profile
from utils.follow.views import FollowMixin
from utils.tutorial.views import TutoMixin


class ProfileDetailView(TutoMixin, ProfileDetailView, MultipleObjectMixin, FollowMixin):

    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        profile = Profile.objects.get(pk=kwargs.pop("pk"))
        if profile.slug and kwargs["slug"] != profile.slug:
            url = profile.get_absolute_url()
            return HttpResponsePermanentRedirect(url)
        kwargs["username"] = profile.user.username
        return super(ProfileDetailView, self).dispatch(request,
                                                       *args, **kwargs)

    def get_context_data(self, **kwargs):
        history = Content.objects.public().filter(author=self.page_user)
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
            "scores": Vote.objects.get_scores_in_bulk(history),
            "nb_fwers": followers.count(),
            "nb_fwees": followers.count(),
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


class ProfileListView(TutoMixin, ProfileListView):

    paginate_by = 15

    def get_queryset(self):
        profiles = self.get_model_class().objects.select_related()

        search_terms = self.request.GET.get("search", "")
        order = self.request.GET.get("order", "")

        if search_terms:
            profiles = profiles.filter(name__icontains=search_terms)
        if order == "date":
            profiles = profiles.order_by("-user__date_joined")
        elif order == "name":
            profiles = profiles.order_by("name")

        return profiles
