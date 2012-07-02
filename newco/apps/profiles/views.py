from django.http import HttpResponsePermanentRedirect
from django.contrib.auth.models import User
from django.views.generic.simple import direct_to_template
from django.views.generic.edit import ProcessFormView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from idios.views import ProfileDetailView
from django.db.models.loading import get_model
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

from items.models import Question, Answer, ExternalLink, Feature
from profiles.models import Profile, Reputation
from follow.models import Follow
from utils.followtools import process_following


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
        if 'follow' in request.POST or 'unfollow' in request.POST:
            if 'follow' in request.POST: # If "follow" send an email to followee
                profile_fwee= kwargs['username'].get_profile()
                profile_fwer=request.user.get_profile()
                
                message_subject = profile_fwee.name + ", " + profile_fwer.name
                message_subject += " vous suit maintenant sur NewCo !"
                                
                txt_template = get_template('follow/_follow_notification_email.txt')
                html_template = get_template('follow/_follow_notification_email.html')
                
                d = Context({ 'profile_followee_name': profile_fwee.name,
                             'message_subject' : message_subject,
                             'profile_follower_url' : profile_fwer.get_absolute_url(),
                             'profile_follower_name' : profile_fwer.name,
                             'profile_followee_url' : profile_fwee.get_absolute_url(),
                             'follower_user' : request.user })
                
                msg_txt = txt_template.render(d)
                msg_html = html_template.render(d)
                
                msg = EmailMultiAlternatives(message_subject, msg_txt, 
                                             'auto-mailer@newco-project.fr', 
                                             [profile_fwee.user.email])
                msg.attach_alternative(msg_html, "text/html")
                msg.send()
            
            return process_following(request)

        else:
            return super(ProfileDetailView, self).post(request,
                                                            *args, **kwargs)
