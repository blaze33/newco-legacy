from django import forms
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.forms.widgets import TextInput
from django.utils.translation import ugettext_lazy as _


class EmailInput(TextInput):
    input_type = "email"


class AskForHelpForm(forms.Form):

    experts = forms.CharField(
        label=_("...some of our experts in this field"), required=False,
        widget=TextInput(attrs={"class": "input-block-level"}),
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
        self.request = kwargs.pop("request", {})
        kwargs.pop("items", {})
        kwargs.pop("tags", {})
        kwargs.pop("prefix", {})
        super(AskForHelpForm, self).__init__(*args, **kwargs)
        if experts_qs:
            ids = map(str, experts_qs.values_list("id", flat=True))
            data_url = "{url}?{get}".format(
                url=reverse("redis", args=["profile"]),
                get="".join(["&id={0}".format(i) for i in ids]))
            self.fields["experts"].widget.attrs.update({"data-url": data_url})
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
