from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponsePermanentRedirect, HttpResponseRedirect

from django.contrib.auth.models import User

from follow.models import Follow
from idios.views import ProfileDetailView, ProfileListView

from items.models import Item, Content
from profiles.models import Profile
from utils.follow.views import ProcessFollowView


class ProcessProfileSearchView(object):

    def post(self, request, *args, **kwargs):
        if "pf_pick" in request.POST:
            name = request.POST["pf_pick"]
            profile_list = Profile.objects.filter(name=name)
            if profile_list.count() == 1:
                response = profile_list[0].get_absolute_url()
            else:
                response = reverse("profile_list") + "?search=" + name
            return HttpResponseRedirect(response)
        else:
            return super(ProcessProfileSearchView, self).post(request,
                                                            *args, **kwargs)


class ProfileDetailView(ProfileDetailView, ProcessProfileSearchView,
                                                            ProcessFollowView):

    def dispatch(self, request, *args, **kwargs):
        profile = Profile.objects.get(pk=kwargs.pop("pk"))
        if profile.slug and kwargs["slug"] != profile.slug:
            url = profile.get_absolute_url()
            return HttpResponsePermanentRedirect(url)
        kwargs["username"] = profile.user.username
        return super(ProfileDetailView, self).dispatch(request,
                                                        *args, **kwargs)

    def get_context_data(self, **kwargs):
        #TODO: better handling of QueryManager

        history = Content.objects.filter(
            Q(author=self.page_user) & Q(status=Content.STATUS.public)
        )

        fwers_ids = Follow.objects.get_follows(
                            self.page_user).values_list("user_id", flat=True)
        obj_fwed = Follow.objects.filter(user=self.page_user)
        fwees_ids = obj_fwed.values_list("target_user_id", flat=True)
        items_fwed_ids = obj_fwed.values_list("target_item_id", flat=True)

        context = super(ProfileDetailView, self).get_context_data(**kwargs)
        context.update({
            "reputation": self.page_user.reputation,
            "history": history.select_subclasses(),
            "fwers": User.objects.filter(pk__in=fwers_ids),
            "fwees": User.objects.filter(pk__in=fwees_ids),
            "items_fwed": Item.objects.filter(pk__in=items_fwed_ids),
            "data_source_profile": Profile.objects.get_all_names(),
        })

        return context


class ProfileListView(ProfileListView, ProcessProfileSearchView):

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
            profiles = profiles.order_by("user__username")

        return profiles

    def get_context_data(self, **kwargs):
        context = super(ProfileListView, self).get_context_data(**kwargs)
        context.update({
            "data_source_profile": Profile.objects.get_all_names()
        })
        return context
