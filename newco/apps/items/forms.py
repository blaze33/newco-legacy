from django.forms import ModelForm
from django.forms.widgets import Textarea
from django.utils.translation import ugettext_lazy as _

from items.models import Item, Question, Answer, Story


class ItemForm(ModelForm):

    create = False

    def __init__(self, *args, **kwargs):
        if 'instance' not in kwargs or kwargs['instance'] == None:
            self.create = True
            self.request = kwargs.pop('request')
            self.user = self.request.user
        return super(ItemForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Item
        exclude = ('author')

    def save(self, commit=True, **kwargs):
        if commit and self.create:
            item = super(ItemForm, self).save(commit=False)
            item.author = self.user
            item.save()
            self.save_m2m()
            return item
        else:
            return super(ItemForm, self).save(commit)


class QuestionForm(ModelForm):

    create = False

    def __init__(self, *args, **kwargs):
        if 'instance' not in kwargs or kwargs['instance'] == None:
            self.create = True
            self.request = kwargs.pop('request')
            self.user = self.request.user
        return super(QuestionForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Question
        exclude = ('author', 'items')
        widgets = {
            'content': Textarea(attrs={
                'class': 'span4',
                'placeholder': _('Ask something specific. Be concise.'),
                'rows': 1}),
        }

    def save(self, commit=True, **kwargs):
        if commit and self.create:
            question = super(QuestionForm, self).save(commit=False)
            question.author = self.user
            question.save()
            question.items.add(kwargs.pop('pk'))
            return question
        else:
            return super(QuestionForm, self).save(commit)


class AnswerForm(ModelForm):

    create = False

    def __init__(self, *args, **kwargs):
        if 'instance' not in kwargs or kwargs['instance'] == None:
            self.create = True
            self.request = kwargs.pop('request')
            self.user = self.request.user
            self.question_id = self.request.REQUEST['question_id']
            self.question = Question.objects.get(pk=self.question_id)
        return super(AnswerForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Answer
        fields = ('content', )
        widgets = {
            'content': Textarea(attrs={
                'class': 'span6',
                'placeholder': _('Be concise and to the point.'),
                'rows': 6}),
        }

    def save(self, commit=True, **kwargs):
        if commit and self.create:
            answer = super(AnswerForm, self).save(commit=False)
            answer.author = self.user
            answer.question = self.question
            answer.save()
            return answer
        else:
            return super(AnswerForm, self).save(commit)


class StoryForm(ModelForm):
    class Meta:
        model = Story
