import re

from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import RedirectView

from django.contrib import messages

from account.utils import user_display

from items.models import Question
from profiles.models import Profile
from utils.mailtools import mail_helper


class AskForHelpView(RedirectView):

    def post(self, request, *args, **kwargs):
        if "ask" not in request.POST:
            return super(AskForHelpView, self).post(request, *args, **kwargs)

        question_id = request.POST.get("question-id", "")

        profile_ids = []
        if request.POST["ask"] == "expert":
            profile_ids.append(int(request.POST["expert-id"]))
        elif request.POST["ask"] == "users":
            profile_ids.extend(
                map(int, re.split("\D+", request.POST["profile-ids"])))

        if not question_id or not profile_ids:
            # sent to logger + fails silenlty
            return HttpResponseRedirect(request.path)

        question = Question.objects.get(id=question_id)

        receiver_profiles = Profile.objects.filter(
            id__in=profile_ids).select_related("user")
        for receiver_profile in receiver_profiles:
            receiver = receiver_profile.user

            # Not worth reloading profile instance
            # receiver_name = user_display(receiver_profile)
            receiver_name = receiver_profile.name

            username = user_display(request.user)
            if receiver != request.user:
                mail_helper(request, receiver, request.user, question)
                kwargs = {"user": username, "receiver": receiver_name}
                display_message("sent", request, **kwargs)
            else:
                display_message("warning", request, user=username)

        return HttpResponseRedirect(request.path)


MESSAGES = {
    "sent": {
        "level": messages.INFO,
        "text": _("{user}, your request has been sent to {receiver}!")
    },
    "warning": {
        "level": messages.WARNING,
        "text": _("{user}, you can't ask yourself to answer a question!")
    },
}


def display_message(msg_type, request, **kwargs):
    messages.add_message(
        request, MESSAGES[msg_type]["level"],
        mark_safe(MESSAGES[msg_type]["text"].format(**kwargs))
    )
