from django.http import HttpResponseRedirect, HttpResponseServerError
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from account.utils import user_display

from voting.models import Vote

from utils.tools import load_object

VOTE_DIRECTIONS = (('up', 1), ('down', -1), ('clear', 0))


def process_voting(request, go_to_object=False):
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

    obj = load_object(request)
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

    try:
        if go_to_object:
            return HttpResponseRedirect(obj.get_absolute_url())
        else:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    except (AttributeError, TypeError):
        if 'HTTP_REFERER' in request.META:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        elif obj:
            return HttpResponseServerError(
                        '"%s" object of type ``%s`` has no method ' + \
                        '``get_absolute_url()``.' % \
                        (unicode(obj), obj.__class__)
            )
        else:
            return HttpResponseServerError(
                        'No follow object and `next` parameter found.'
            )