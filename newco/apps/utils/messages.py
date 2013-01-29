from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _, pgettext

from django.contrib import messages

from account.utils import user_display

MESSAGES = {
    "object-created": {
        "level": messages.SUCCESS,
        "text": _("Thanks {user}, {article}{verbose_name} was successfully "
                  "{created}.")
    },
    "object-updated": {
        "level": messages.INFO,
        "text": _("Thanks {user}, {article}{verbose_name} was successfully "
                  "{updated}.")
    },
    "about": {
        "level": messages.INFO,
        "text": _("Thanks {user}, your bio has been successfully updated.")
    },
    "form-invalid": {
        "level": messages.ERROR,
        "text": _("Warning {user}, the form is invalid.")
    },
    "follow": {
        "level": messages.INFO,
        "text": _("{user}, you are now following {object}.")
    },
    "unfollow": {
        "level": messages.INFO,
        "text": _("{user}, you are not following {object} anymore.")
    },
    "follow-warning": {
        "level": messages.WARNING,
        "text": _("{user}, you can't follow yourself!")
    },
    "email-sent": {
        "level": messages.INFO,
        "text": _("{user}, your request has been sent to {receiver}!")
    },
    "ask-warning": {
        "level": messages.WARNING,
        "text": _("{user}, you can't ask yourself to answer a question!")
    },
    "email-error": {
        "level": messages.ERROR,
        "text": _("{user}, {email} is not a valid email address!")
    },
    "vote-up": {
        "level": messages.INFO,
        "text": _("{user}, your up vote on {object} has been recorded.")
    },
    "vote-down": {
        "level": messages.INFO,
        "text": _("{user}, your down vote on {object} has been recorded.")
    },
    "vote-clear": {
        "level": messages.INFO,
        "text": _("{user}, your vote on {object} has been cancelled.")
    },
    "vote-warning": {
        "level": messages.WARNING,
        "text": _("{user}, you can't vote on your own contribution!")
    },
}


def add_message(key, request, **kwargs):
    kwargs = update_kwargs(key, request, **kwargs)
    messages.add_message(request, MESSAGES[key]["level"],
                         mark_safe(MESSAGES[key]["text"].format(**kwargs)))


def render_messages(request):
    context = {"messages": messages.get_messages(request)}
    return render_to_string("pinax_theme_bootstrap:_messages.html", context)


def update_kwargs(key, request, **kwargs):
    kwargs.update({"user": user_display(request.user)})
    if "model" in kwargs:
        model = kwargs.pop("model")
        kwargs.update({"article": pgettext(model._meta.module_name, "the "),
                       "verbose_name": model._meta.verbose_name})
        if key == "object-created":
            word = "created"
        elif key == "object-updated":
            word = "updated"
        kwargs.update({word: pgettext(model._meta.module_name, word)})
    return kwargs
