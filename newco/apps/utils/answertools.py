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
#                mail_answeree(profile,
#                    request.user.get_profile(), request.META.get('HTTP_HOST'), question, answer
#                )
                
               
            except KeyError:
                raise AttributeError(
                    "Mail has not been sent."
                )
            return HttpResponseRedirect(request.META.get('HTTP_REFERER')) 
        else:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER')) 
    else:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER')) 

def mail_answeree(answeree, answerer, site, question, answer):
    message_subject = "%s, %s a repondu a votre question !" % \
                            (answeree.name, answerer.name)

    txt_template = get_template('answer/_answer_notification_email.txt')
    html_template = get_template('answer/_answer_notification_email.html')

    txt_req = _('answered your question "%(question)s"') % \
                                                {"question": question.content}

    items = question.items.select_related()
    nb_items = items.count()
    if nb_items == 1:
        item=items[0]
        txt_req = txt_req + " " + _("about the product %(product)s.") % \
                                                {"product": item.name}
    elif nb_items > 1:
        print nb_items
        txt_req = txt_req + " " + ugettext("on")
        for i, item in enumerate(items):
            print i
            txt_req = txt_req + " " + item.name
            if i < 4 and i != (nb_items - 1):
                txt_req = txt_req + ","
            elif i == 4:
                if nb_items > 4:
                    txt_req = txt_req + "..."
                break

    d = Context({'answeree': answeree.name, 'answerer': answerer.name,
        'answeree_url': "http://%s%s" % (site, answeree.get_absolute_url()),
        'answerer_url': "http://%s%s" % (site, answerer.get_absolute_url()),
        'message_subject': message_subject,
        'question_object':question,
        "product_object":items[0].name,
        'question_url':"http://%s%s" % (site, question.get_absolute_url()),
        "product_url":"http://%s%s" % (site, item.get_absolute_url()),
        "txt_request": txt_req,
        'answer_object':answer
    })

    msg_txt = txt_template.render(d)
    msg_html = html_template.render(d)

    msg = EmailMultiAlternatives(message_subject, msg_txt,
        'auto-mailer@newco-project.fr', [answeree.user.email]
    )
    msg.attach_alternative(msg_html, "text/html")
    
    waiting_time=timedelta(minutes=1)
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
