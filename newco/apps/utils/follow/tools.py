from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from django.contrib import messages

from account.utils import user_display
from follow.utils import toggle
from follow.models import Follow

from utils.mailtools import mail_followee


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
                mail_followee(request, follow.target, request.user)
            title = user_display(follow.target)
        else:
            title = unicode(follow.target)

        msg = "follow" if is_following else "unfollow"
        messages.add_message(request, msgs[msg]["level"], mark_safe(
            msgs[msg]["text"] % {"user": username, "object": title}))
    else:
        messages.add_message(request, msgs["warning"]["level"], mark_safe(
            msgs["warning"]["text"] % {"user": username}))

    return HttpResponseRedirect(success_url)
