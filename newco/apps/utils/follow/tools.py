import json

from django.http import HttpResponse, HttpResponseRedirect
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from django.contrib import messages
from django.contrib.auth.models import User

from account.utils import user_display
from follow.utils import follow, unfollow
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

    user = request.user
    username = user_display(user)
    if not user == obj:
        is_following = Follow.objects.is_following(user, obj)
        follow_obj = unfollow(user, obj) if is_following else follow(user, obj)
        is_following = not is_following

        if follow_obj.target.__class__ is User:
            if is_following:
                mail_followee(request, follow_obj.target, user)
            title = user_display(follow_obj.target)
        else:
            title = unicode(follow_obj.target)

        msg = "follow" if is_following else "unfollow"
        messages.add_message(request, msgs[msg]["level"], mark_safe(
            msgs[msg]["text"] % {"user": username, "object": title}))
    else:
        messages.add_message(request, msgs["warning"]["level"], mark_safe(
            msgs["warning"]["text"] % {"user": username}))

    data = {"is_following": is_following, "message": "success"}
    if request.is_ajax():
        return HttpResponse(json.dumps(data), mimetype="application/json")
    else:
        return HttpResponseRedirect(success_url)
