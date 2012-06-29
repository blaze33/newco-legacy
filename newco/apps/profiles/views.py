from django.http import HttpResponsePermanentRedirect
from django.contrib.auth.models import User
from django.views.generic.edit import ProcessFormView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from idios.views import ProfileDetailView

from items.models import Question, Answer, ExternalLink, Feature
from profiles.models import Profile, Reputation
from follow.models import Follow
from utils.followtools import process_following


class ProfileDetailView(ProfileDetailView, ProcessFormView):

    def dispatch(self, request, *args, **kwargs):
        profile = Profile.objects.get(pk=kwargs.pop('pk'))
        if profile.slug and kwargs['slug'] != profile.slug:
            url = profile.get_absolute_url()
            return HttpResponsePermanentRedirect(url)
        kwargs['username'] = profile.user
        return super(ProfileDetailView, self).dispatch(request,
                                                        *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProfileDetailView, self).get_context_data(**kwargs)
        context['reputation'] = Reputation.objects.get(user=self.object.user)

        history = list(Question.objects.filter(author=self.object.user))
        history.extend(Answer.objects.filter(author=self.object.user))
        history.extend(ExternalLink.objects.filter(author=self.object.user))
        history.extend(Feature.objects.filter(author=self.object.user))
        context['history'] = sorted(history, key=lambda c: c.pub_date,
                                                            reverse=True)

        fwers_ids = Follow.objects.get_follows(
                self.object.user).values_list('user_id', flat=True)
        context['fwers'] = User.objects.filter(pk__in=fwers_ids)

        fwees_ids = Follow.objects.filter(
                user=self.object.user).values_list('target_user_id', flat=True)
        context['fwees'] = User.objects.filter(pk__in=fwees_ids)

        #content ordering for newsfeed
        newsfeed = list(Question.objects.filter(author__in=fwees_ids))
        newsfeed.extend(Answer.objects.filter(author__in=fwees_ids))
        newsfeed.extend(ExternalLink.objects.filter(author__in=fwees_ids))
        newsfeed.extend(Feature.objects.filter(author__in=fwees_ids))
        context['newsfeed'] = sorted(newsfeed, key=lambda c: c.pub_date,
                                                            reverse=True)

        return context

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        if 'follow' in request.POST:
            return process_following(request)
        else:
            return super(ProfileDetailView, self).post(request,
                                                            *args, **kwargs)
