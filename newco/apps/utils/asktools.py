from django.http import HttpResponseRedirect
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from account.utils import user_display


def process_asking(request, obj, success_url):
    msgs = {
        "ask": {
            "level": messages.INFO,
            "text": _("%(user)s, your request has been sent to %(ask_profile)s !")
        },
        "warning": {
            "level": messages.WARNING,
            "text": _("%(user)s, your request has not been sent, you can't ask yourself!")
        },
    }

    if "ask" in request.POST:
        requested_user = User.objects.get(id=request.POST["ask"])
        requested_profile = requested_user.get_profile()

    #TODO: improve typeahead
#    elif "ask_prof_pick" in request.POST:
#        ask_profile_search = request.POST["ask_prof_pick"]
#        profile_list = Profile.objects.filter(name=ask_profile_search)
#        if profile_list.count() > 0:
#            profile = profile_list[0]
#        else:
#            pass

    username = user_display(request.user)

    if requested_user != request.user:
        mail_askee(requested_profile, request.user.get_profile(),
                                            request.META.get('HTTP_HOST'), obj)
        messages.add_message(request,
            msgs["ask"]["level"],
            msgs["ask"]["text"] % {
                "user": username, "ask_profile": requested_profile
            }
        )
    else:
        messages.add_message(request,
            msgs["warning"]["level"],
            msgs["warning"]["text"] % {"user": username}
        )

    return HttpResponseRedirect(success_url)


def mail_askee(askee, asker, site, obj):
    message_subject = "%s, %s vous demande une reponse !" % \
                            (askee.name, asker.name)

    txt_template = get_template('ask/_ask_notification_email.txt')
    html_template = get_template('ask/_ask_notification_email.html')

    d = Context({'askee': askee.name, 'asker': asker.name,
        'askee_url': "http://%s%s" % (site, askee.get_absolute_url()),
        'asker_url': "http://%s%s" % (site, asker.get_absolute_url()),
        'message_subject': message_subject,
        'question_object': obj
    })

    msg_txt = txt_template.render(d)
    msg_html = html_template.render(d)

    msg = EmailMultiAlternatives(message_subject, msg_txt,
        'auto-mailer@newco-project.fr', [askee.user.email]
    )
    msg.attach_alternative(msg_html, "text/html")
    msg.send()
