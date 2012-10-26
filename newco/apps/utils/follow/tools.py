from django.http import HttpResponseRedirect
from django.template.loader import get_template
from django.template import Context
from django.utils.translation import ugettext_lazy as _

from django.contrib import messages

from account.utils import user_display
from follow.utils import toggle
from follow.models import Follow

from utils.mailtools import send_mail


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

    username = user_display(request.user)
    if not request.user == obj:
        follow = toggle(request.user, obj)

        is_following = Follow.objects.is_following(request.user, obj)

        if follow.target._meta.object_name == "User":
            if is_following:
                mail_followee(follow.target, request.user,
                              request.META.get('HTTP_HOST'))
            object_unicode = user_display(follow.target)
        else:
            object_unicode = unicode(follow.target)

        msg = "follow" if is_following else "unfollow"
        messages.add_message(
            request, msgs[msg]["level"],
            msgs[msg]["text"] % {"user": username, "object": object_unicode}
        )
    else:
        messages.add_message(
            request, msgs["warning"]["level"],
            msgs["warning"]["text"] % {"user": username}
        )

    return HttpResponseRedirect(success_url)


def mail_followee(fwee, fwer, site):
    fwee_name = user_display(fwee)
    fwer_name = user_display(fwer)

    msg_subject = "%s, %s vous suit maintenant sur NewCo !" % \
                  (fwee_name, fwer_name)

    txt_template = get_template("mail/_follow_notification_email.txt")
    html_template = get_template("mail/_follow_notification_email.html")

    context = Context({
        "followee": fwee_name, "follower": fwer_name,
        "followee_url": "http://%s%s" % (site, fwee.get_absolute_url()),
        "follower_url": "http://%s%s" % (site, fwer.get_absolute_url()),
        "message_subject": msg_subject
    })

    send_mail(msg_subject, fwee, txt_template, html_template, context)
