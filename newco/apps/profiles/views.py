from django.http import HttpResponsePermanentRedirect
from django.http import HttpResponseRedirect, HttpResponseServerError
from django.contrib.auth.models import User
from django.views.generic.base import RedirectView
from django.views.generic.simple import direct_to_template
from django.core.urlresolvers import reverse
from django.views.generic.edit import ProcessFormView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from idios.views import ProfileDetailView
from django.db.models.loading import get_model

from items.models import Question, Answer, ExternalLink, Feature
from profiles.models import Profile, Reputation
from follow.models import Follow
from follow.utils import toggle


class ProfileDetailView(ProfileDetailView, ProcessFormView):

    def get(self, request, *args, **kwargs): 
        
        if 'username' in kwargs: # case: url = profiles/profile/##/slug 
            return super(ProfileDetailView, self).get(self,
                                                    request,
                                                    *args,
                                                    **kwargs)
        
        elif request.user.is_authenticated(): # case url = homepage
            self.template_name = "homepage_logged.html"
            self.page_user = request.user
            self.object = self.page_user.get_profile()
            context = self.get_context_data()
            context.update({'kwargs': kwargs})
            return self.render_to_response(context)
       
        else:
            return direct_to_template(request, "homepage.html")

    def dispatch(self, request, *args, **kwargs):
        if 'pk' in kwargs: #only useful if user is in a "profile" view, not on homepage
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
            app_label = request.POST['app_label']
            object_name = request.POST['object_name']
            pk = request.POST['pk']
            model = get_model(app_label, object_name)
            obj = model._default_manager.get(pk=pk)
            follow = toggle(request.user, obj)
            try:
                # Might be something better to do
                # than follow.target.get_absolute_url()
                return HttpResponseRedirect(follow.target.get_absolute_url())
            except (AttributeError, TypeError):
                if 'HTTP_REFERER' in request.META:
                    return HttpResponseRedirect(
                            request.META.get('HTTP_REFERER', '/')
                    )
                elif follow:
                    return HttpResponseServerError(
                            '"%s" object of type ``%s`` has no method ' + \
                            '``get_absolute_url()``.' % \
                            (unicode(follow.target), follow.target.__class__))
                else:
                    return HttpResponseServerError(
                            'No follow object and `next` parameter found.'
                )
        else:
            return super(ProfileDetailView, self).post(request,
                                                            *args, **kwargs)
