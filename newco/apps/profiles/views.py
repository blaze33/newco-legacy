from django.http import HttpResponsePermanentRedirect
from django.contrib.auth.models import User
from django.views.generic.simple import direct_to_template
from django.views.generic.edit import ProcessFormView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from idios.views import ProfileDetailView

from items.models import Item, Question, Answer, ExternalLink, Feature
from profiles.models import Profile, Reputation
from follow.models import Follow
from utils.followtools import process_following


class ProfileDetailView(ProfileDetailView, ProcessFormView):

    is_profile_page = True

    def get(self, request, *args, **kwargs):
        if self.is_profile_page:
            return super(ProfileDetailView, self).get(self,
                                                    request,
                                                    *args,
                                                    **kwargs)
        elif request.user.is_authenticated():
            self.template_name = "profiles/profile_homepage.html"
            self.page_user = request.user
            self.object = self.page_user.get_profile()
            context = self.get_context_data()
            context.update({'kwargs': kwargs})
            return self.render_to_response(context)
        else:
            return direct_to_template(request, "homepage.html")

    def dispatch(self, request, *args, **kwargs):
        if self.is_profile_page:
            profile = Profile.objects.get(pk=kwargs.pop('pk'))
            if profile.slug and kwargs['slug'] != profile.slug:
                url = profile.get_absolute_url()
                return HttpResponsePermanentRedirect(url)
            kwargs['username'] = profile.user
        return super(ProfileDetailView, self).dispatch(request,
                                                        *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProfileDetailView, self).get_context_data(**kwargs)

        history = list()
        for model in [Question, Answer, ExternalLink, Feature]:
            history.extend(model.objects.filter(author=self.object.user))

        fwers_ids = Follow.objects.get_follows(
                self.object.user).values_list('user_id', flat=True)
        obj_fwed = Follow.objects.filter(user=self.object.user)
        fwees_ids = obj_fwed.values_list('target_user_id', flat=True)
        items_fwed_ids = obj_fwed.values_list('target_item_id', flat=True)

        #content ordering for newsfeed
        newsfeed = list(Answer.objects.filter(Q(author__in=fwees_ids) |
            Q(id__in=Question.objects.filter(
                items__in=items_fwed_ids).values_list('answer', flat=True)
            )
        ))
        for model in [Question, ExternalLink, Feature]:
            newsfeed.extend(model.objects.filter(
                    Q(author__in=fwees_ids) | Q(items__in=items_fwed_ids)
                ).exclude(author=self.object.user)
            )

        context.update({
            'reputation': Reputation.objects.get(user=self.object.user),
            'history': sorted(history, key=lambda c: c.pub_date, reverse=True),
            'fwers': User.objects.filter(pk__in=fwers_ids),
            'fwees': User.objects.filter(pk__in=fwees_ids),
            'items_fwed': Item.objects.filter(pk__in=items_fwed_ids),
            'newsfeed': sorted(newsfeed, key=lambda c: c.pub_date,
                                                            reverse=True)
        })

        return context

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        if 'follow' in request.POST or 'unfollow' in request.POST:
            return process_following(request, go_to_object=False)
        else:
            return super(ProfileDetailView, self).post(request,
                                                            *args, **kwargs)
