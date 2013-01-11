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

        expert_id = request.POST.get("expert-id", "")
        question_id = request.POST.get("question-id", "")
        if not question_id or not expert_id:
            # sent to logger + fails silenlty
            return HttpResponseRedirect(request.path)

        question = Question.objects.get(id=question_id)

        receiver_profile = Profile.objects.get(id=expert_id)
        receiver = receiver_profile.user
        receiver_name = user_display(receiver_profile)

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
