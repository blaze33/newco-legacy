from django.forms import ModelForm
from django.forms.widgets import Textarea
from django.utils.translation import ugettext_lazy as _

from items.models import Item, Question, Answer, Story, ExternalLink, FeatureP, FeatureN


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


class ExternalLinkForm(ModelForm):
    create = False

    def __init__(self, *args, **kwargs):
        if 'instance' not in kwargs or kwargs['instance'] == None:
            self.create = True
            self.request = kwargs.pop('request')
            self.user = self.request.user
            self.item_id = self.request.REQUEST['item_id']
            self.item = Item.objects.get(pk=self.item_id)
            
        return super(ExternalLinkForm, self).__init__(*args, **kwargs)

    class Meta:
        model = ExternalLink
        exclude = ('author', 'items')
        widgets = {
            'text': Textarea(attrs={
                'class': 'span4',
                'placeholder': _('Descriptif du lien'), 
                'rows': 1}),
        }

    def save(self, commit=True, **kwargs):
        if commit and self.create:
            extlink = super(ExternalLinkForm, self).save(commit=False)
            extlink.author = self.user
            extlink.save()
            extlink.items.add(self.item_id)
            return extlink
        else:
            return super(ExternalLinkForm, self).save(commit)

class FeaturePForm(ModelForm):

    create = False

    def __init__(self, *args, **kwargs):
        if 'instance' not in kwargs or kwargs['instance'] == None:
            self.create = True
            self.request = kwargs.pop('request')
            self.user = self.request.user
            self.item_id = self.request.REQUEST['item_id']
            self.item = Item.objects.get(pk=self.item_id)
        return super(FeaturePForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FeatureP
        exclude = ('author', 'items')
        widgets = {
            'content': Textarea(attrs={
                'class': 'span4',
                'placeholder': _('Please add a feature'), 
                'rows': 1}),
        }

    def save(self, commit=True, **kwargs):
        if commit and self.create:
            featurep = super(FeaturePForm, self).save(commit=False)
            featurep.author = self.user
            featurep.save()
            featurep.items.add(self.item_id)
            return featurep
        else:
            return super(FeaturePForm, self).save(commit)
        
        
class FeatureNForm(ModelForm):

    create = False

    def __init__(self, *args, **kwargs):
        if 'instance' not in kwargs or kwargs['instance'] == None:
            self.create = True
            self.request = kwargs.pop('request')
            self.user = self.request.user
            self.item_id = self.request.REQUEST['item_id']
            self.item = Item.objects.get(pk=self.item_id)
        return super(FeatureNForm, self).__init__(*args, **kwargs)

    class Meta:
        model = FeatureN
        exclude = ('author', 'items')
        widgets = {
            'content': Textarea(attrs={
                'class': 'span4',
                'placeholder': _('Please add a feature'), 
                'rows': 1}),
        }

    def save(self, commit=True, **kwargs):
        if commit and self.create:
            featuren = super(FeatureNForm, self).save(commit=False)
            featuren.author = self.user
            featuren.save()
            featuren.items.add(self.item_id)
            return featuren
        else:
            return super(FeatureNForm, self).save(commit)
