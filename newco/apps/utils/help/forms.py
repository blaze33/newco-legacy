from django import forms
from django.core.exceptions import ValidationError
from django.forms.widgets import TextInput, SelectMultiple
from django.utils.translation import ugettext_lazy as _

from profiles.models import Profile


class AskForHelpForm(forms.Form):

    experts = forms.ModelMultipleChoiceField(
        queryset=Profile.objects.all(), required=False,
        widget=SelectMultiple(attrs={"class": "input-block-level"}))
    users = forms.CharField(
        widget=TextInput(attrs={"class": "input-block-level"}), required=False)
    email = forms.EmailField(
        widget=TextInput(attrs={"class": "input-block-level"}), required=False)

    def __init__(self, experts_qs, *args, **kwargs):
        super(AskForHelpForm, self).__init__(*args, **kwargs)
        self.fields["experts"].queryset = experts_qs

    def clean(self):
        cleaned_data = super(AskForHelpForm, self).clean()
        values = cleaned_data.values()
        if not any(values) and len(values) == 3:
            self._errors["experts"] = self.error_class([""])
            self._errors["users"] = self.error_class([""])
            self._errors["email"] = self.error_class([""])
            raise ValidationError(_("Choose at least one field to fill"))
        return cleaned_data
