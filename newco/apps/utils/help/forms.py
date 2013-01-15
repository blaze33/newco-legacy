from django import forms
from django.core.exceptions import ValidationError
from django.forms.widgets import TextInput, SelectMultiple
from django.utils.translation import ugettext_lazy as _

from profiles.models import Profile


class EmailInput(TextInput):
    input_type = "email"


class AskForHelpForm(forms.Form):

    experts = forms.ModelMultipleChoiceField(
        label=_("...some of our experts in this field"), required=False,
        queryset=Profile.objects.all(),
        widget=SelectMultiple(attrs={"class": "input-block-level"}),
        help_text=_("These are users that have declared being competent on "
                    "this particular field"))
    users = forms.CharField(
        label=_("...users you know"), required=False,
        widget=TextInput(attrs={"class": "input-block-level"}))
    email = forms.EmailField(
        label=_("...a non-member through an email"), required=False,
        widget=EmailInput(attrs={"placeholder": _(
            "Enter an email address"), "class": "input-block-level"}))

    def __init__(self, experts_qs, *args, **kwargs):
        super(AskForHelpForm, self).__init__(*args, **kwargs)
        if experts_qs:
            self.fields["experts"].queryset = experts_qs
        else:
            del self.fields["experts"]

    def clean(self):
        cleaned_data = super(AskForHelpForm, self).clean()
        values = cleaned_data.values()
        if not any(values) and len(values) == 3:
            self._errors["experts"] = self.error_class([""])
            self._errors["users"] = self.error_class([""])
            self._errors["email"] = self.error_class([""])
            raise ValidationError(_("Fill at least one field"))
        return cleaned_data
