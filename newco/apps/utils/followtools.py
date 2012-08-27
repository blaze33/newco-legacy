from django.http import HttpResponseRedirect
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from account.utils import user_display

from follow.utils import toggle
from follow.models import Follow

from utils.tools import load_object


def process_following(request, obj, success_url):
    msgs = {
        "follow": {
            "level": messages.INFO,
            "text": _("%(user)s, you are now following %(object)s.")
        },
        "unfollow": {
            "level": messages.INFO,
            "text": _("%(user)s, you are not following %(object)s anymore.")
        },
        "warning": {
            "level": messages.WARNING,
            "text": _("%(user)s, you can't follow yourself!")
        },
    }

    obj = load_object(request)
    username = user_display(request.user)
    if not request.user == obj:
        follow = toggle(request.user, obj)

        is_following = Follow.objects.is_following(request.user, obj)

        if follow.target._meta.module_name == 'user':
            if is_following:
                mail_followee(follow.target.get_profile(),
                    request.user.get_profile(), request.META.get('HTTP_HOST')
                )
            object_unicode = user_display(follow.target)
        else:
            object_unicode = follow.target

        msg = "follow" if is_following else "unfollow"
        messages.add_message(request,
            msgs[msg]["level"],
            msgs[msg]["text"] % {"user": username, "object": object_unicode}
        )
    else:
        follow = None
        messages.add_message(request,
            msgs["warning"]["level"],
            msgs["warning"]["text"] % {"user": username}
        )

    return HttpResponseRedirect(success_url)


def mail_followee(fwee, fwer, site):
    message_subject = "%s, %s vous suit maintenant sur NewCo !" % \
                            (fwee.name, fwer.name)

    txt_template = get_template('follow/_follow_notification_email.txt')
    html_template = get_template('follow/_follow_notification_email.html')

    d = Context({'followee': fwee.name, 'follower': fwer.name,
        'followee_url': "http://%s%s" % (site, fwee.get_absolute_url()),
        'follower_url': "http://%s%s" % (site, fwer.get_absolute_url()),
        'message_subject': message_subject
    })

    msg_txt = txt_template.render(d)
    msg_html = html_template.render(d)

    msg = EmailMultiAlternatives(message_subject, msg_txt,
        'auto-mailer@newco-project.fr', [fwee.user.email]
    )
    msg.attach_alternative(msg_html, "text/html")
    msg.send()
