from django.utils.translation import ugettext_lazy as _, pgettext
from django.utils.safestring import mark_safe

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
}


def display_message(key, request, **kwargs):
    kwargs = update_kwargs(key, request, **kwargs)
    messages.add_message(request, MESSAGES[key]["level"],
                         mark_safe(MESSAGES[key]["text"].format(**kwargs)))


def get_message(key, request, **kwargs):
    kwargs = update_kwargs(key, request, **kwargs)
    message = messages.storage.base.Message(
        MESSAGES[key]["level"],
        mark_safe(MESSAGES[key]["text"].format(**kwargs)))
    message._prepare()
    return {"text": message.message, "tags": message.tags}


def update_kwargs(key, request, **kwargs):
    kwargs.update({"user": user_display(request.user)})
    if "model" in kwargs:
        model = kwargs.pop("model")
        kwargs.update({"article": pgettext(model._meta.module_name, "the "),
                       key: pgettext(model._meta.module_name, key),
                       "verbose_name": model._meta.verbose_name})
    return kwargs
