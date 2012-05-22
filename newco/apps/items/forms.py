from django.forms import ModelForm

from items.models import Item, Question, Answer

class ItemForm(ModelForm):

    class Meta:
        model = Item


class QuestionForm(ModelForm):

    class Meta:
        model = Question


class AnswerForm(ModelForm):

    class Meta:
        model = Answer
