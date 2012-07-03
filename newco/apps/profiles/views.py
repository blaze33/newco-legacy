from django.http import HttpResponsePermanentRedirect
from django.contrib.auth.models import User
from django.views.generic.simple import direct_to_template
from django.views.generic.edit import ProcessFormView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from idios.views import ProfileDetailView

from items.models import Question, Answer, ExternalLink, Feature, Item
from profiles.models import Profile, Reputation
from follow.models import Follow
from utils.followtools import process_following, mail_followee


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
        
        fweds_ids = Follow.objects.filter(
                user=self.object.user).values_list('target_item_id', flat=True)
        context['fweds'] = Item.objects.filter(pk__in=fweds_ids)

        
        #content ordering for newsfeed
        newsfeed = list(Question.objects.filter(
                Q(author__in=fwees_ids)|
                Q(items__in=fweds_ids)
        ))
        question_list = Question.objects.filter(items__in=fweds_ids) #Request to get answers from followed objects
        newsfeed.extend(Answer.objects.filter(
                Q(author__in=fwees_ids)|
                Q(id__in=question_list.values_list('answer', flat=True))
        ))
        newsfeed.extend(ExternalLink.objects.filter(
                Q(author__in=fwees_ids)|
                Q(items__in=fweds_ids)
        ))
        newsfeed.extend(Feature.objects.filter(
                Q(author__in=fwees_ids)|
                Q(items__in=fweds_ids)
        ))
        context['newsfeed'] = sorted(newsfeed, key=lambda c: c.pub_date,
                                                            reverse=True)

        return context

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        if 'follow' in request.POST or 'unfollow' in request.POST:
            if 'follow' in request.POST:
                mail_followee(kwargs['username'].get_profile(),
                    request.user.get_profile(), request.META.get('HTTP_HOST')
                )
            return process_following(request)
        else:
            return super(ProfileDetailView, self).post(request,
                                                            *args, **kwargs)
