from django.forms import ModelForm

from items.models import Item, Question


class ItemForm(ModelForm):

    class Meta:
        model = Item


class QuestionForm(ModelForm):

    class Meta:
        model = Question
