from django.forms import RegexField
from django.utils.translation import ugettext_lazy as _

from account.forms import SignupForm


class SignupForm(SignupForm):

    profile_name = RegexField(label=_("Profile name"), max_length=30,
        regex=r'^[\w.@+-]+$',
        help_text=_("Required. 30 characters or fewer. Letters, digits and "
                      "@/./+/-/_ only."),
        error_messages={
        'invalid': _("This value may contain only letters, numbers and "
                     "@/./+/-/_ characters.")}
    )

    class Meta:
        fields = ('email', 'password1', 'password2', 'profile_name')

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        del self.fields["username"]
        self.fields.keyOrder = [
            'email', 'password', 'password_confirm', 'profile_name',
        ]

