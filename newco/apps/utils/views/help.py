import re

from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import RedirectView

from django.contrib import messages
from django.contrib.auth.models import User

from account.models import Account
from account.utils import user_display

from items.models import Question
from profiles.models import Profile
from utils.constants import EMAIL_PATTERN
from utils.mailtools import mail_helper


def void():
    return ""


class AskForHelpView(RedirectView):

    def post(self, request, *args, **kwargs):
        if "ask" not in request.POST:
            return super(AskForHelpView, self).post(request, *args, **kwargs)

        question_id = request.POST.get("question-id", "")
        if not question_id:
            # sent to logger + fails silenlty
            return HttpResponseRedirect(request.path)

        case = request.POST["ask"]
        question = Question.objects.get(id=question_id)
        username = user_display(request.user)
        profile_ids = []

        if case == "email":
            receiver_profiles = []
            m = EMAIL_PATTERN.match(request.POST["email"])
            if m:
                receiver_profile = Profile(user=User(email=m.group()),
                                           name=m.group("username"))
                receiver_profile.user.account = Account()
                receiver_profile.user.get_absolute_url = void
                receiver_profiles.append(receiver_profile)
            else:
                kwargs = {"user": username, "email": request.POST["email"]}
                display_message("email", request, **kwargs)
        elif case == "expert" or case == "users":
            if case == "expert":
                profile_ids.append(int(request.POST["expert-id"]))
            elif case == "users":
                profile_ids.extend(
                    map(int, re.split("\D+", request.POST["profile-ids"])))
            receiver_profiles = Profile.objects.filter(
                id__in=profile_ids).select_related("user")

        for receiver_profile in receiver_profiles:
            receiver = receiver_profile.user

            receiver_name = user_display(receiver_profile)

            if receiver != request.user:
                mail_helper(request, receiver, request.user, question,
                            receiver_name, username)
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
    "email": {
        "level": messages.ERROR,
        "text": _("{user}, {email} is not a valid email address!")
    },
}


def display_message(msg_type, request, **kwargs):
    messages.add_message(
        request, MESSAGES[msg_type]["level"],
        mark_safe(MESSAGES[msg_type]["text"].format(**kwargs))
    )
