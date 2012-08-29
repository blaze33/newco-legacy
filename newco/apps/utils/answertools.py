from django.db import models
from django.http import HttpResponseRedirect, HttpResponseServerError
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.contrib.auth.models import User
from django.template import Context
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from account.utils import user_display
from django.utils import timezone
from datetime import datetime, timedelta

from follow.utils import toggle
from follow.models import Follow
from profiles.models import Profile
from about.models import LastMail
from items.models import Question

from utils.tools import load_object


def process_answering(request, go_to_object=False):
    question_id=request.POST["question_id"]
    question=Question.objects.filter(pk=question_id)[0]
    answer=request.POST["content"]
    profile_list=Profile.objects.filter(name=question.author)
    if profile_list:
        profile=profile_list[0]
        if profile != request.user.get_profile():
            try:        
                mail_answeree(profile,
                    request.user.get_profile(), request.META.get('HTTP_HOST'), question, answer
                )
                
               
            except KeyError:
                raise AttributeError(
                    "Mail has not been sent."
                )
            return HttpResponseRedirect(request.META.get('HTTP_REFERER')) 
        else:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER')) 
    else:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER')) 

def mail_answeree(answeree, answerer, site, object, answer):
    message_subject = "%s, %s a repondu a votre question !" % \
                            (answeree.name, answerer.name)

    txt_template = get_template('answer/_answer_notification_email.txt')
    html_template = get_template('answer/_answer_notification_email.html')

    d = Context({'answeree': answeree.name, 'answerer': answerer.name,
        'answeree_url': "http://%s%s" % (site, answeree.get_absolute_url()),
        'answerer_url': "http://%s%s" % (site, answerer.get_absolute_url()),
        'message_subject': message_subject,
        'question_object':object,
        'question_url':"http://%s%s" % (site, object.get_absolute_url()),
        'answer_object':answer
    })

    msg_txt = txt_template.render(d)
    msg_html = html_template.render(d)

    msg = EmailMultiAlternatives(message_subject, msg_txt,
        'auto-mailer@newco-project.fr', [answeree.user.email]
    )
    msg.attach_alternative(msg_html, "text/html")
    
    waiting_time=timedelta(minutes=10)
    last_modif=LastMail.objects.filter(user=answerer.user)
    if last_modif:
        last_mail = last_modif[0]
        diff=timezone.now()-last_mail.modified
        print diff
        if diff > waiting_time:
            msg.send()
            last_mail.save()
    else:
        last_mail = LastMail.objects.get_or_create(user=answerer.user)[0]
        msg.send()
        last_mail.save()
