from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from django.contrib import messages

from account.utils import user_display

from voting.models import Vote

from items.models import Content, Question, Answer

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

        Vote.objects.record_vote(obj.select_parent(), request.user, vote)
        if obj.__class__ is Content:
            obj = obj.select_subclass()
        if obj.__class__ is Question:
            obj.sort_related_answers()
        elif obj.__class__ is Answer:
            obj.question.sort_related_answers()

        messages.add_message(request, msgs[direction]["level"], mark_safe(
            msgs[direction]["text"] % {"user": username, "object": obj}))
    else:
        messages.add_message(request, msgs["warning"]["level"], mark_safe(
            msgs["warning"]["text"] % {"user": username}))

    return HttpResponseRedirect(success_url)
