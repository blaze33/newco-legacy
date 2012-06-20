from django.forms import CharField
from django.utils.translation import ugettext_lazy as _

from account.forms import SignupForm


class SignupForm(SignupForm):

    profile_name = CharField(label=_("Profile name"), max_length=30,
        help_text=_("Required. 30 characters or fewer."),
        error_messages={'max_length': _("No more than 30 characters.")}
    )

    class Meta:
        fields = ('email', 'password1', 'password2', 'profile_name')

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        del self.fields["username"]
        self.fields.keyOrder = [
            'email', 'password', 'password_confirm', 'profile_name',
        ]
