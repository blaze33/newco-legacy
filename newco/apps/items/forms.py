from django.core.exceptions import ValidationError
from django.forms.fields import ChoiceField
from django.forms.models import (ModelForm, BaseInlineFormSet,
                                 inlineformset_factory)
from django.forms.widgets import Textarea, RadioSelect, SelectMultiple
from django.utils.translation import (ugettext_lazy as _, ungettext_lazy,
                                      pgettext_lazy)

from model_utils import Choices
from newco_bw_editor.widgets import BW_small_Widget
from taggit.forms import TagWidget

from affiliation.models import AffiliationItem
from affiliation.tools import stores_product_search
from items.models import Item, Content, Question, Answer
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
        item = super(ItemForm, self).save(commit=False)
        if self.create:
            item.author = self.request.user

        if commit:
            item.save()
            self.save_m2m()

        self.unlink_aff(item)
        self.link_aff(item)

        return item

    def link_aff(self, item):
        aff_ids = self.request.POST.getlist("link_aff", [])
        AffiliationItem.objects.filter(id__in=aff_ids).update(item=item)

    def unlink_aff(self, item):
        aff_ids = self.request.POST.getlist("linked_aff", [])
        item.affiliationitem_set.exclude(id__in=aff_ids).delete()

    def stores_search(self):
        self.errors.clear()
        keyword = self.data["name"]
        self.product_list_by_store = stores_product_search(keyword)

    def reload_current_search(self):
        self.product_list_by_store = _reload_current_search(self)


class QuestionForm(ModelForm):

    PARENTS = Choices(
        ("items", "products", pgettext_lazy("parent", "products")),
        ("tags", "tags", pgettext_lazy("parent", "tags"))
    )

    max_tags = 10
    max_products = 5
    PRODUCTS_HELP_TEXT = ungettext_lazy(
        "Select {max} product using Tab or Enter, and the Arrow keys.",
        "Select up to {max} products using Tab or Enter, and the Arrow keys.",
        max_products)

    create = False
    no_results = _("No results matched")
    parents = ChoiceField(widget=RadioSelect, choices=PARENTS,
                          label=_("My question refers to"))

    class Meta:
        model = Question
        fields = ("content", "parents", "items", "tags")
        widgets = {
            "content": Textarea(attrs={
                "class": "input-block-level", "rows": 2,
                "placeholder": _("Ask something specific.")}),
            "items": SelectMultiple(attrs={"class": "input-block-level"}),
            "tags": TagWidget(attrs={"class": "input-block-level"})
        }

    class Media:
        css = {
            "all": ("css/question_form.css",)
        }
        js = ("js/question_form.js",)

    def __init__(self, request, *args, **kwargs):
        default_status = Content._meta.get_field("status").default
        self.status = kwargs.pop("status", default_status)
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.request, self.object = [request, kwargs.get("instance", None)]
        self.create = True if not self.object else False
        if self.object:
            if self.object.items.all():
                self.fields["parents"].initial = self.PARENTS.products
            elif self.object.tags.all():
                self.fields["parents"].initial = self.PARENTS.tags
        self.fields["items"].help_text = self.PRODUCTS_HELP_TEXT.format(
            max=self.max_products)

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
            if len(tags) > self.max_tags:
                tags_msg = _("Pick less than %d tags" % self.max_tags)
                self._errors["tags"] = self.error_class([tags_msg])
                del cleaned_data["tags"]
            elif len(items) > self.max_products:
                items_msg = _("Pick less than %d products" % self.max_products)
                self._errors["items"] = self.error_class([items_msg])
                del cleaned_data["items"]
        return cleaned_data


class PartialQuestionForm(ModelForm):

    class Meta:
        model = Question
        fields = ("content", )
        widgets = {"content": Textarea(attrs={
            "rows": 1, "placeholder": _("Ask something specific.")})}

    def __init__(self, request, items=[], tags=[], *args, **kwargs):
        kwargs.pop("experts_qs", {})
        super(PartialQuestionForm, self).__init__(*args, **kwargs)
        self.request, self.items, self.tags = [request, items, tags]
        if not request.user.is_authenticated():
            self.fields["content"].widget.attrs.update({
                "disabled": "",
                "placeholder": _("Please log in before asking your question.")
            })

    def save(self, commit=True, **kwargs):
        question = super(PartialQuestionForm, self).save(commit=False)
        question.author = self.request.user

        if commit:
            question.save()
            self.save_m2m()
            question.items.add(*self.items)
            question.tags.add(*self.tags)
        return question


class AnswerForm(ModelForm):

    create = False

    class Meta:
        model = Answer
        fields = ("content", )
        widgets = {
            "content": BW_small_Widget(attrs={
                "rows": 10, "class": "wysiwyg", "rel": "bw_editor_small",
                "placeholder": _("Be concise and to the point.")}),
        }

    class Media:
        css = {
            "all": ("css/answer_form.css",)
        }

    def __init__(self, request, *args, **kwargs):
        kwargs.pop("experts_qs", {})
        kwargs.pop("items", {})
        default_status = Content._meta.get_field("status").default
        self.status = kwargs.pop("status", default_status)
        super(AnswerForm, self).__init__(*args, **kwargs)
        self.request, self.object = [request, kwargs.get("instance", None)]
        self.create = True if not self.object else False
        if "instance" in kwargs:
            self.question = kwargs["instance"].question
        elif "question-id" in request.POST:
            question_id = request.POST["question-id"]
            self.question = Question.objects.get(id=question_id)
        self.fields["content"].label = ""
        if not request.user.is_authenticated():
            self.fields["content"].widget.attrs.update({"disabled": ""})

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


def _reload_current_search(item_form):
    store_dict = {}
    for key in item_form.request.POST.keys():
        if "current_search_" in key:
            store = unicode.replace(key, "current_search_", "")
            aff_ids = item_form.request.POST.getlist(key)
            store_dict.update({store: AffiliationItem.objects.filter(
                id__in=aff_ids, item=None)})
    return store_dict
