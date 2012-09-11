from django.core.exceptions import ObjectDoesNotExist
from django.forms import ModelForm
from django.forms.widgets import Textarea
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from chosen.forms import ChosenSelectMultiple
from newco_bw_editor.widgets import BW_small_Widget

from affiliation.models import AffiliationItem, AffiliationItemCatalog
from affiliation.tools import stores_product_search
from items.models import Item, Question, Answer, Story, Link, Feature


class ItemForm(ModelForm):

    create = False

    class Meta:
        model = Item
        exclude = ("author")

    def __init__(self, *args, **kwargs):
        if "request" in kwargs:
            self.request = kwargs.pop("request")
            self.reload_current_search()
        if "instance" not in kwargs or kwargs["instance"] == None:
            self.create = True
            self.user = self.request.user
        return super(ItemForm, self).__init__(*args, **kwargs)

    def save(self, commit=True, **kwargs):
        if commit and self.create:
            item = super(ItemForm, self).save(commit=False)
            item.author = self.user
            item.save()
            self.save_m2m()
        else:
            item = super(ItemForm, self).save(commit)

        self.link_aff(item)

        return item

    def link_aff(self, item):
        if hasattr(self, "request"):
            _link_aff(self.request, item)

    def stores_search(self):
        self.errors.clear()
        keyword = self.data["name"]
        self.product_list_by_store = stores_product_search(keyword)

    def reload_current_search(self):
        self.product_list_by_store = _reload_current_search(self)


class QuestionForm(ModelForm):

    create = False
    no_results = _("No results matched")

    class Meta:
        model = Question
        fields = ("content", "status", "items")
        help_text = {"items": _("Pick a product.")}
        widgets = {
            "content": Textarea(attrs={
                "class": "span4",
                "placeholder": _("Ask something specific."),
                "rows": 1}),
            "items": ChosenSelectMultiple(attrs={"class": "span4", "rows": 1},
                overlay=_("Pick a product.")),
        }

    def __init__(self, *args, **kwargs):
        if 'instance' not in kwargs or kwargs['instance'] == None:
            self.create = True
            self.request = kwargs.pop('request')
            self.user = self.request.user
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.fields["items"].help_text = _(
            "Select one or several products using Enter and the Arrow keys")
        if hasattr(self, "request"):
            if self.request.GET.get("fields", "") != "add_items":
                del self.fields["items"]
        else:
            del self.fields["items"]

    def save(self, commit=True, **kwargs):
        if commit and self.create:
            question = super(QuestionForm, self).save(commit=False)
            question.author = self.user
            question.save()
            if "items" in self.fields:
                self.save_m2m()
            else:
                question.items.add(kwargs.pop("pk"))
            return question
        else:
            return super(QuestionForm, self).save(commit)


class AnswerForm(ModelForm):

    create = False

    class Meta:
        model = Answer
        fields = ("content", "status", )
        widgets = {
            "content": BW_small_Widget(attrs={
                "class": "span4",
                "rows": 6,
                "placeholder": _("Be concise and to the point."),
                "rel": "bw_editor_small",
            }),
        }

    def __init__(self, *args, **kwargs):
        if "instance" not in kwargs or kwargs["instance"] == None:
            self.create = True
            self.request = kwargs.pop("request")
            self.user = self.request.user
            if "question_id" in self.request.REQUEST:
                self.question_id = self.request.REQUEST["question_id"]
                self.question = Question.objects.get(pk=self.question_id)
        else:
            self.object = kwargs["instance"]
            self.question = self.object.question
        return super(AnswerForm, self).__init__(*args, **kwargs)

    def save(self, commit=True, **kwargs):
        if commit and self.create:
            answer = super(AnswerForm, self).save(commit=False)
            answer.author = self.user
            answer.question = self.question
            answer.save()
            answer.items = answer.question.items.all()
            return answer
        else:
            return super(AnswerForm, self).save(commit)


class StoryForm(ModelForm):
    class Meta:
        model = Story


class LinkForm(ModelForm):

    create = False

    class Meta:
        model = Link
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
        return super(LinkForm, self).__init__(*args, **kwargs)

    def save(self, commit=True, **kwargs):
        if commit and self.create:
            link = super(LinkForm, self).save(commit=False)
            link.author = self.user
            link.save()
            link.items.add(self.item_id)
            return link
        else:
            return super(LinkForm, self).save(commit)


class FeatureForm(ModelForm):

    create = False

    class Meta:
        model = Feature
        fields = ('content', 'status', )
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
            self.positive = (self.request.REQUEST['positive'] == 'True')
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


def _link_aff(request, item):
    if "link_aff" in request.POST:
        aff_cat_ids = request.POST.getlist("link_aff")
        for aff_cat_id in aff_cat_ids:
            try:
                aff_cat = AffiliationItemCatalog.objects.get(
                                                        id=aff_cat_id)
            except ObjectDoesNotExist:
                pass
            else:
                aff_item, c = AffiliationItem.objects.get_or_create(
                        item=item, store=aff_cat.store,
                        object_id=aff_cat.object_id
                )
                aff_item.copy_from_affcatalog(aff_cat)
                aff_item.save()


def _reload_current_search(item_form):
    product_list_by_store = dict()
    for key in item_form.request.POST.keys():
        if "current_search_" in key:
            store = unicode.replace(key, "current_search_", "")
            aff_cat_ids = item_form.request.POST.getlist(key)
            product_list = list()
            for aff_cat_id in aff_cat_ids:
                try:
                    aff_cat = AffiliationItemCatalog.objects.get(
                                                            id=aff_cat_id)
                except ObjectDoesNotExist:
                    pass
                else:
                    product_list.append(aff_cat)
            product_list_by_store.update({store: product_list})
    return product_list_by_store
