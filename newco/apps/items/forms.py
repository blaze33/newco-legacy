from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.forms.fields import ChoiceField
from django.forms.models import (ModelForm, BaseInlineFormSet,
                                 inlineformset_factory)
from django.forms.widgets import Textarea, RadioSelect, SelectMultiple
from django.utils.translation import ugettext_lazy as _, pgettext

from account.utils import user_display
from model_utils import Choices
from newco_bw_editor.widgets import BW_small_Widget
from taggit.forms import TagWidget

from affiliation.models import AffiliationItem, AffiliationItemCatalog
from affiliation.tools import stores_product_search
from items.models import Item, Content, Question, Answer, Story, Link
from utils.mailtools import mail_question_author


class ItemForm(ModelForm):

    create = False

    class Meta:
        model = Item
        exclude = ("author")
        widgets = {"tags": TagWidget(attrs={"class": "input-block-level"})}

    def __init__(self, request, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        self.request, self.object = [request, kwargs.get("instance", None)]
        self.create = True if not self.object else False
        self.reload_current_search()

    def save(self, commit=True, **kwargs):
        if commit and self.create:
            item = super(ItemForm, self).save(commit=False)
            item.author = self.request.user
            item.save()
            self.save_m2m()
        else:
            item = super(ItemForm, self).save(commit)

        self.link_aff(item)

        return item

    def link_aff(self, item):
        _link_aff(self.request, item)

    def stores_search(self):
        self.errors.clear()
        keyword = self.data["name"]
        self.product_list_by_store = stores_product_search(keyword)

    def reload_current_search(self):
        self.product_list_by_store = _reload_current_search(self)


class QuestionForm(ModelForm):

    PARENTS = Choices(
        ("0", "products", pgettext("parent", "products")),
        ("1", "tags", pgettext("parent", "tags"))
    )

    create = False
    no_results = _("No results matched")
    parents = ChoiceField(widget=RadioSelect, choices=PARENTS,
                          label=_("My question refers to"))

    class Meta:
        model = Question
        fields = ("content", "parents", "items", "tags")
        widgets = {
            "content": Textarea(attrs={
                "class": "input-block-level",
                "placeholder": _("Ask something specific."),
                "rows": 2}),
            "items": SelectMultiple(
                attrs={"class": "input-block-level", "rows": 1},
                # overlay=_("Pick a product."),
            ),
            "tags": TagWidget(attrs={"class": "input-block-level"})
        }

    def __init__(self, request, *args, **kwargs):
        default_status = Content._meta.get_field("status").default
        self.status = kwargs.pop("status", default_status)
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.request, self.object = [request, kwargs.get("instance", None)]
        self.create = True if not self.object else False
        if self.object:
            self.fields.get("parents").initial = self.PARENTS.products \
                if self.object.items.count() else self.PARENTS.tags
        self.fields.get("items").help_text = _(
            "Select up to 5 products using Tab or Enter, and the Arrow keys.")

    def save(self, commit=True, **kwargs):
        question = super(QuestionForm, self).save(commit=False)
        if self.create:
            question.author = self.request.user
        question.status = self.status

        if commit:
            question.save()
            self.save_m2m()
        return question

    def clean(self):
        cleaned_data = super(QuestionForm, self).clean()
        parents = cleaned_data.get("parents")

        if parents == self.PARENTS.tags:
            cleaned_data["items"] = []
        elif parents == self.PARENTS.products:
            cleaned_data["tags"] = []
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


class PartialQuestionForm(ModelForm):

    class Meta:
        model = Question
        fields = ("content", )
        widgets = {"content": Textarea(attrs={
            "class": "span4", "rows": 1,
            "placeholder": _("Ask something specific.")})}

    def __init__(self, request, item, *args, **kwargs):
        super(PartialQuestionForm, self).__init__(*args, **kwargs)
        self.request, self.item = [request, item]

    def save(self, commit=True, **kwargs):
        question = super(PartialQuestionForm, self).save(commit=False)
        question.author = self.request.user

        if commit:
            question.save()
            self.save_m2m()
            question.items.add(self.item.id)
        return question


class AnswerForm(ModelForm):

    create = False

    class Meta:
        model = Answer
        fields = ("content", )
        widgets = {
            "content": BW_small_Widget(attrs={
                "rows": 10,
                "style": "width: 100%; box-sizing: border-box;",
                "placeholder": _("Be concise and to the point."),
                "rel": "bw_editor_small",
            }),
        }

    def __init__(self, request, *args, **kwargs):
        default_status = Content._meta.get_field("status").default
        self.status = kwargs.pop("status", default_status)
        super(AnswerForm, self).__init__(*args, **kwargs)
        self.request, self.object = [request, kwargs.get("instance", None)]
        self.create = True if not self.object else False
        question_id = request.REQUEST.get("question_id", 0)
        self.question = Question.objects.get(id=question_id) if question_id \
            else getattr(self.object, "question", None)

        if self.request.user.is_authenticated():
            profile = self.request.user.get_profile()
            label = user_display(self.request.user)
            label = label + ", " + profile.about if profile.about else label
        else:
            label = _("Please login before answering.")
        self.fields["content"].label = label

    def save(self, commit=True, **kwargs):
        answer = super(AnswerForm, self).save(commit=False)

        if self.create:
            answer.author = self.request.user
            if not answer.question and hasattr(self, "question"):
                answer.question = self.question
        answer.status = self.status

        if commit:
            answer.save()
            if self.create and answer.is_public:
                mail_question_author(self.request, answer)

        return answer


class BaseQAFormSet(BaseInlineFormSet):
    def __init__(self, request, status=None, empty_permitted=True,
                 *args, **kwargs):
        self.request, self.status = [request, status]
        self.empty_permitted = empty_permitted
        super(BaseQAFormSet, self).__init__(*args, **kwargs)

    def _construct_forms(self):
        # override method to add request/empty_permitted/status arguments
        # for AnswerForm init
        kwargs = {}
        for field in ["request", "empty_permitted", "status"]:
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
    product_list_by_store = {}
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
