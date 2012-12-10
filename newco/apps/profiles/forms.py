from django.forms.models import ModelForm

from taggit.forms import TagWidget

from profiles.models import Profile


class ProfileForm(ModelForm):

    class Meta:
        model = Profile
        exclude = ("user")
        widgets = {"skills": TagWidget(attrs={"class": "input-block-level"})}
