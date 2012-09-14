from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from account.utils import user_display

from voting.models import Vote

VOTE_DIRECTIONS = (('up', 1), ('down', -1), ('clear', 0))


def process_voting(request, obj, success_url):
    msgs = {
        "up": {
            "level": messages.INFO,
            "text": _("%(user)s, your up vote on %(object)s has been recorded.")
        },
        "down": {
            "level": messages.INFO,
            "text": _("%(user)s, your down vote on %(object)s has been recorded.")
        },
        "clear": {
            "level": messages.INFO,
            "text": _("%(user)s, your vote on %(object)s has been cancelled.")
        },
        "warning": {
            "level": messages.WARNING,
            "text": _("%(user)s, you can't vote on your own contribution!")
        },
    }

    direction = request.POST['vote_button']
    username = user_display(request.user)

    if obj.author != request.user:
        try:
            vote = dict(VOTE_DIRECTIONS)[direction]
        except KeyError:
            raise AttributeError(
                "'%s' is not a valid vote type." % direction
            )

        Vote.objects.record_vote(obj, request.user, vote)

        messages.add_message(request,
            msgs[direction]["level"],
            msgs[direction]["text"] % {"user": username, "object": obj}
        )
    else:
        messages.add_message(request,
            msgs["warning"]["level"],
            msgs["warning"]["text"] % {"user": username}
        )

    return HttpResponseRedirect(success_url)
