from django.forms import ModelForm
from django.forms.widgets import Textarea
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from items.models import Item, Question, Answer, Story, ExternalLink, Feature


class ItemForm(ModelForm):

    create = False

    class Meta:
        model = Item
        exclude = ('author')

    def __init__(self, *args, **kwargs):
        if 'instance' not in kwargs or kwargs['instance'] == None:
            self.create = True
            self.request = kwargs.pop('request')
            self.user = self.request.user
        return super(ItemForm, self).__init__(*args, **kwargs)

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

    class Meta:
        model = Question
        exclude = ('author', 'items')
        widgets = {
            'content': Textarea(attrs={
                'class': 'span4',
                'placeholder': _('Ask something specific. Be concise.'),
                'rows': 1}),
        }

    def __init__(self, *args, **kwargs):
        if 'instance' not in kwargs or kwargs['instance'] == None:
            self.create = True
            self.request = kwargs.pop('request')
            self.user = self.request.user
        return super(QuestionForm, self).__init__(*args, **kwargs)

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

    class Meta:
        model = Answer
        fields = ('content', )
        widgets = {
            'content': Textarea(attrs={
                'class': 'span6',
                'placeholder': _('Be concise and to the point.'),
                'rows': 6}),
        }

    def __init__(self, *args, **kwargs):
        if 'instance' not in kwargs or kwargs['instance'] == None:
            self.create = True
            self.request = kwargs.pop('request')
            self.user = self.request.user
            self.question_id = self.request.REQUEST['question_id']
            self.question = Question.objects.get(pk=self.question_id)
        else:
            self.object = kwargs['instance']
            self.question = self.object.question
        return super(AnswerForm, self).__init__(*args, **kwargs)

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


class ExternalLinkForm(ModelForm):

    create = False

    class Meta:
        model = ExternalLink
        exclude = ('author', 'items')
        widgets = {
            'text': Textarea(attrs={
                'class': 'span4',
                'placeholder': _('Link description'),
                'rows': 1}),
        }

    def __init__(self, *args, **kwargs):
        if 'instance' not in kwargs or kwargs['instance'] == None:
            self.create = True
            self.request = kwargs.pop('request')
            self.user = self.request.user
            self.item_id = self.request.REQUEST['item_id']
            self.item = Item.objects.get(pk=self.item_id)
        else:
            self.object = kwargs['instance']
            self.item = self.object.items.select_related()[0]
        return super(ExternalLinkForm, self).__init__(*args, **kwargs)

    def save(self, commit=True, **kwargs):
        if commit and self.create:
            link = super(ExternalLinkForm, self).save(commit=False)
            link.author = self.user
            link.save()
            link.items.add(self.item_id)
            return link
        else:
            return super(ExternalLinkForm, self).save(commit)


class FeatureForm(ModelForm):

    create = False

    class Meta:
        model = Feature
        fields = ('content', )
        widgets = {
            'content': Textarea(attrs={
                'class': 'span4',
                'rows': 1}),
        }

    def __init__(self, *args, **kwargs):
        if 'instance' not in kwargs or kwargs['instance'] == None:
            self.create = True
            self.request = kwargs.pop('request')
            self.user = self.request.user
            self.positive = bool(self.request.REQUEST['positive'] == True)
            self.item_id = self.request.REQUEST['item_id']
            self.item = Item.objects.get(pk=self.item_id)
        else:
            self.object = kwargs['instance']
            self.positive = self.object.positive
            self.item = self.object.items.select_related()[0]
        if hasattr(self, "positive"):
            if self.positive:
                self.way = _("positive")
                self._meta.widgets['content'].attrs['placeholder'] = ugettext(
    'What feature do you like?'
)
            else:
                self.way = _("negative")
                self._meta.widgets['content'].attrs['placeholder'] = ugettext(
    'What feature do you dislike?'
)
        return super(FeatureForm, self).__init__(*args, **kwargs)

    def save(self, commit=True, **kwargs):
        if commit and self.create:
            feature = super(FeatureForm, self).save(commit=False)
            feature.author = self.user
            feature.positive = self.positive
            feature.save()
            feature.items.add(self.item_id)
            return feature
        else:
            return super(FeatureForm, self).save(commit)
