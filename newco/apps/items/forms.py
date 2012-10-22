from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.forms.models import (ModelForm, BaseInlineFormSet,
                                 inlineformset_factory)
from django.forms.widgets import Textarea
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from chosen.forms import ChosenSelect, ChosenSelectMultiple
from newco_bw_editor.widgets import BW_small_Widget
from taggit.forms import TagField
from taggit_autosuggest.widgets import TagAutoSuggest

from affiliation.models import AffiliationItem, AffiliationItemCatalog
from affiliation.tools import stores_product_search
from items.models import Item, Content, Question, Answer, Story, Link, Feature


class ItemForm(ModelForm):

    create = False
    tag_field = Item._meta.get_field_by_name('tags')[0]
    tags = TagField(required=not(tag_field.blank),
                    help_text=tag_field.help_text,
                    label=capfirst(tag_field.verbose_name),
                    widget=TagAutoSuggest())

    class Meta:
        model = Item
        exclude = ("author")

    def __init__(self, *args, **kwargs):
        if "request" in kwargs:
            self.request = kwargs.pop("request")
            self.user = self.request.user
            self.reload_current_search()
        if "instance" not in kwargs or kwargs["instance"] is None:
            self.create = True
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
    tag_field = Content._meta.get_field_by_name('tags')[0]
    tags = TagField(required=not(tag_field.blank),
                    help_text=tag_field.help_text,
                    label=capfirst(tag_field.verbose_name),
                    widget=TagAutoSuggest(attrs={"class": "span4"}))

    class Meta:
        model = Question
        fields = ("content", "status", "items", "tags")
        widgets = {
            "content": Textarea(attrs={
                "class": "span4",
                "placeholder": _("Ask something specific."),
                "rows": 1}),
            "status": ChosenSelect(attrs={"class": "span4"}),
            "items": ChosenSelectMultiple(
                attrs={"class": "span4", "rows": 1},
                overlay=_("Pick a product."),
            )
        }

    def __init__(self, *args, **kwargs):
        if "request" in kwargs:
            self.request = kwargs.pop("request")
            self.user = self.request.user
        if "instance" not in kwargs or kwargs["instance"] is None:
            self.create = True
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.fields.get("items").help_text = _(
            "Select one or several products using Enter and the Arrow keys.")

    def save(self, commit=True, **kwargs):
        if self.create:
            question = super(QuestionForm, self).save(commit=False)
            question.author = self.user
            if commit:
                question.save()
                self.save_m2m()
            return question
        else:
            return super(QuestionForm, self).save(commit)

    def clean(self):
        cleaned_data = super(QuestionForm, self).clean()
        tags, items = [cleaned_data.get("tags"), cleaned_data.get("items")]

        if not tags and not items or tags and items:
            self._errors["tags"] = self.error_class([""])
            self._errors["items"] = self.error_class([""])
            if tags:
                raise ValidationError(_("Choose between either products or "
                                        "tags to link your question to."))
            else:
                raise ValidationError(_("Link your question to at least either"
                                        " one product or one tag."))
        else:
            if len(tags) > 5:
                tags_msg = _("Pick less than 5 tags")
                self._errors["tags"] = self.error_class([tags_msg])
                del cleaned_data["tags"]
            elif len(items) > 10:
                items_msg = _("Pick less than 10 items")
                self._errors["items"] = self.error_class([items_msg])
                del cleaned_data["items"]

        return cleaned_data


class AnswerForm(ModelForm):

    create = False

    class Meta:
        model = Answer
        fields = ("content", "status", )
        widgets = {
            "content": BW_small_Widget(attrs={
                "rows": 10,
                "style": "width: 100%; box-sizing: border-box;",
                "placeholder": _("Be concise and to the point."),
                "rel": "bw_editor_small",
            }),
        }

    def __init__(self, *args, **kwargs):
        if "request" in kwargs:
            self.request = kwargs.pop("request")
            self.user = self.request.user
            if "question_id" in self.request.REQUEST:
                self.question_id = self.request.REQUEST.get("question_id")
                self.question = Question.objects.get(id=self.question_id)
        if "instance" not in kwargs or kwargs["instance"] is None:
            self.create = True
        else:
            self.object = kwargs["instance"]
            self.question = self.object.question
        super(AnswerForm, self).__init__(*args, **kwargs)
        self.fields['content'].label = _("Your answer")

    def save(self, commit=True, **kwargs):
        if self.create:
            answer = super(AnswerForm, self).save(commit=False)
            answer.author = self.user
            if not answer.question and hasattr(self, "question"):
                answer.question = self.question
            if commit:
                answer.save()
                answer.items = answer.question.items.all()
            return answer
        else:
            return super(AnswerForm, self).save(commit)


class BaseQAFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        self.empty_permitted = kwargs.pop("empty_permitted", None)
        super(BaseQAFormSet, self).__init__(*args, **kwargs)

    def _construct_forms(self):
        # override method to add request/empty_permitted arguments
        # for AnswerForm init
        kwargs = {}
        for field in ["request", "empty_permitted"]:
            value = getattr(self, field, None)
            if value is not None:
                kwargs.update({field: value})
        self.forms = []
        for i in xrange(self.total_form_count()):
            self.forms.append(self._construct_form(i, **kwargs))


QAFormSet = inlineformset_factory(Question, Answer, form=AnswerForm,
                                  formset=BaseQAFormSet, fk_name="question",
                                  can_delete=False, extra=1, max_num=1)


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
        if 'instance' not in kwargs or kwargs['instance'] is None:
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
                    if AffiliationItem.objects.filter(
                            object_id=aff_cat.object_id,
                            store=aff_cat.store).count() == 0:
                        product_list.append(aff_cat)
            product_list_by_store.update({store: product_list})
    return product_list_by_store
