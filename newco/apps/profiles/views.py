from django.http import HttpResponsePermanentRedirect
from django.http import HttpResponseRedirect, HttpResponseGone
from django.contrib.auth.models import User
from django.views.generic.base import RedirectView
from django.core.urlresolvers import reverse
from idios.views import ProfileDetailView

from items.models import Question, Answer, ExternalLink, Feature
from profiles.models import Reputation
from follow.models import Follow


class ProfileRedirectView(RedirectView):

    def get(self, request, *args, **kwargs):
        if 'username' in kwargs:
            username = kwargs['username']
            profile = User.objects.get(username=username).get_profile()
            url = reverse('profile_detail_full', kwargs={
                'username': username, 'slug': profile.slug}
            )
        if url:
            if self.permanent:
                return HttpResponsePermanentRedirect(url)
            else:
                return HttpResponseRedirect(url)
        else:
            return HttpResponseGone()


class ProfileDetailView(ProfileDetailView):

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
