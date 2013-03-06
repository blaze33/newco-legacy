from django.forms import CharField
from django.utils.translation import ugettext_lazy as _

from account.forms import SignupForm


class SignupForm(SignupForm):

    first_name = CharField(
        label=_("First name") + " *", max_length=30, required=False,
        error_messages={"max_length": _("No more than 30 characters.")})
    last_name = CharField(
        label=_("Last name") + " *", max_length=30, required=False,
        help_text=_("* Optionnal"),
        error_messages={"max_length": _("No more than 30 characters.")})

    profile_name = CharField(
        label=_("Profile name"), max_length=30, help_text=_(
            "30 characters tops. Can be whatever you want. "
            "And can be modified."),
        error_messages={"max_length": _("No more than 30 characters.")})

    class Meta:
        fields = ("email", "password1", "password2",
                  "first_name", "last_name", "profile_name")

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        del self.fields["username"]
        self.fields.keyOrder = ["email", "password", "password_confirm",
                                "first_name", "last_name", "profile_name"]
