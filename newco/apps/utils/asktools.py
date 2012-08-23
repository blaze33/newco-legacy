from django.http import HttpResponseRedirect, HttpResponseServerError
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from account.utils import user_display

from follow.utils import toggle
from follow.models import Follow
from profiles.models import Profile

from utils.tools import load_object


def process_asking(request, go_to_object=False):
    msgs = {
        "ask": {
            "level": messages.INFO,
            "text": _("%(user)s, your message has been sent to %(ask_profile)s !")
        },    
            
        "warning": {
            "level": messages.INFO,
            "text": _("%(user)s, your message has not been sent, you can't asking yourself !")
        },
    }
    
    obj = load_object(request)
    if 'ask' in request.POST:
        ask_profile = request.POST["ask"]
        profile_list= Profile.objects.filter(name=ask_profile)
        profile=profile_list[0]

    elif 'ask_prof_pick' in request.POST:
        ask_profile_search = request.POST["ask_prof_pick"]
        profile_list = Profile.objects.filter(name=ask_profile_search)
        if profile_list.count() > 0:
            profile = profile_list[0]     
        else:
            pass

        username = user_display(request.user)

    if profile != request.user.get_profile():
        try:        
            mail_askee(profile,
                request.user.get_profile(), request.META.get('HTTP_HOST'), obj
            )
            
            messages.add_message(request,
            msgs["ask"]["level"],
            msgs["ask"]["text"] % {"user": username, "ask_profile":profile }
        )
        except KeyError:
            raise AttributeError(
                "Mail has not been sent."
            )
    
    else:
        messages.add_message(request,
            msgs["warning"]["level"],
            msgs["warning"]["text"] % {"user": username}
        )

    if go_to_object:
            return HttpResponseRedirect(obj.get_absolute_url()) 
    else:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



def mail_askee(askee, asker, site, object):
    message_subject = "%s, %s vous demande une reponse !" % \
                            (askee.name, asker.name)

    txt_template = get_template('ask/_ask_notification_email.txt')
    html_template = get_template('ask/_ask_notification_email.html')

    d = Context({'askee': askee.name, 'asker': asker.name,
        'askee_url': "http://%s%s" % (site, askee.get_absolute_url()),
        'asker_url': "http://%s%s" % (site, asker.get_absolute_url()),
        'message_subject': message_subject,
        'question_object':object
    })

    msg_txt = txt_template.render(d)
    msg_html = html_template.render(d)

    msg = EmailMultiAlternatives(message_subject, msg_txt,
        'auto-mailer@newco-project.fr', [askee.user.email]
    )
    msg.attach_alternative(msg_html, "text/html")
    msg.send()
