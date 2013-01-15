import re

from django.db.models.query import EmptyQuerySet
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from account.models import Account
from account.utils import user_display

from items.models import Question
from profiles.models import Profile
from utils.constants import EMAIL_PATTERN
from utils.help.forms import AskForHelpForm
from utils.mailtools import mail_helper


def void():
    return ""


class AskForHelpMixin(object):

    form_class = AskForHelpForm
    experts = EmptyQuerySet(model=Profile)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(ask_form=form))

    def form_valid(self, form):
        receiver_profiles = []
        request, user = [self.request, self.request.user]
        question = Question.objects.get(id=form.question_id)
        username = user_display(user)

        for key, value in form.cleaned_data.items():
            if key == "experts" and value:
                receiver_profiles.extend(value)
            elif key == "users" and value:
                profile_ids = map(int, re.split("\D+", value))
                receiver_profiles.extend(Profile.objects.filter(
                    id__in=profile_ids).select_related("user"))
            elif key == "email" and value:
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

        for receiver_profile in receiver_profiles:
            receiver = receiver_profile.user

            receiver_name = user_display(receiver_profile)

            if receiver != user:
                mail_helper(request, receiver, user, question, receiver_name,
                            username)
                kwargs = {"user": username, "receiver": receiver_name}
                display_message("sent", request, **kwargs)
            else:
                display_message("warning", request, user=username)

        return HttpResponseRedirect(request.path)

    def get_form_kwargs(self):
        kwargs = super(AskForHelpMixin, self).get_form_kwargs()
        kwargs.update({"experts_qs": self.experts})
        return kwargs

    def get_context_data(self, **kwargs):
        form = kwargs.pop("ask_form", None)
        if not form:
            form_class = self.get_form_class()
            form = self.get_form(form_class)
        kwargs.update({"ask_form": form})
        return super(AskForHelpMixin, self).get_context_data(**kwargs)

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        if "ask" not in request.POST:
            return super(AskForHelpMixin, self).post(request, *args, **kwargs)

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        form.question_id = request.POST.get("question-id", "")
        if not form.question_id:
            # sent to logger + fails silenlty
            return HttpResponseRedirect(request.path)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


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
