from django.forms import ModelForm
from django.forms import Textarea

from items.models import Item, Question, Answer, Story

class ItemForm(ModelForm):

    class Meta:
        model = Item


class QuestionForm(ModelForm):

    class Meta:
        model = Question


class AnswerForm(ModelForm):

    class Meta:
        model = Answer


class StoryForm(ModelForm):

    class Meta:
        model = Story
        widgets = {
            'content': Textarea(attrs={'rows': 5}),
        }
