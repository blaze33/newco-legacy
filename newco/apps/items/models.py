import datetime
from collections import OrderedDict

from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Count
from django.template.defaultfilters import slugify, truncatechars
from django.utils import timezone
from django.utils.datastructures import SortedDict
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User
from django.contrib.contenttypes import generic

from django_extensions.db.models import TimeStampedModel
from follow.utils import register
from taggit.managers import TaggableManager
from taggit.models import Tag

from content.models import VoteModel
from items import QUERY_STR_PATTERNS, ANCHOR_PATTERNS, STATUSES
from items.managers import ContentManager, ItemManager
from utils.vote import Vote

CONTENT_URL_PATTERN = "%(path)s?%(query_string)s#%(anchor)s"
TAG_VERBOSE_NAME = _("Tags")
TAG_HELP_TEXT = _("Add one or several related categories/activities using"
                  " Tab or Enter, and the Arrow keys.")


class Item(TimeStampedModel):
    name = models.CharField(_("name"), max_length=255)
    slug = models.SlugField(_("slug"), editable=False)
    author = models.ForeignKey(User, verbose_name=_("author"), null=True)
    tags = TaggableManager(TAG_VERBOSE_NAME, help_text=TAG_HELP_TEXT)

    objects = ItemManager()

    class Meta:
        verbose_name = _("product")

    def __init__(self, *args, **kwargs):
        super(Item, self).__init__(*args, **kwargs)
        self._image = None
        self._node = None

    def __unicode__(self):
        return u"%s" % (self.name)

    def save(self):
        maxl = self._meta.get_field_by_name("slug")[0].max_length
        self.slug = truncatechars(slugify(self.name), maxl)
        super(Item, self).save()

    def get_absolute_url(self):
        return reverse("item_detail",
                       args=[self._meta.module_name, self.id, self.slug])

    def get_image(self):
        if self._image is None:
            self._image = self.node.graph.get_image()
        return self._image

    def set_image(self, value):
        self._image = value

    def del_image(self):
        del self._image
    image = property(get_image, set_image, del_image, "Image property")

    def get_node(self):
        if self._node is None:
            self._node = sync_products(Item, self)
        return self._node

    def set_node(self, value):
        self._node = value

    def del_node(self):
        del self._node
    node = property(get_node, set_node, del_node, "Node property")
register(Item)


class Content(VoteModel):
    author = models.ForeignKey(User, verbose_name=_("author"), null=True)
    status = models.SmallIntegerField(_("status"), choices=STATUSES,
                                      default=STATUSES.public)
    items = models.ManyToManyField(Item, verbose_name=_("products"),
                                   blank=True)
    tags = TaggableManager(TAG_VERBOSE_NAME, help_text=TAG_HELP_TEXT,
                           blank=True)

    objects = ContentManager()

    class Meta:
        ordering = ["-created"]

    @property
    def is_public(self):
        return self.status == STATUSES.public

    @property
    def is_draft(self):
        return self.status == STATUSES.draft

    @property
    def anchor(self):
        return ANCHOR_PATTERNS.get(self.__class__.__name__) % self.__dict__

    @property
    def query_string(self):
        return QUERY_STR_PATTERNS.get(self.__class__.__name__) % self.__dict__

    def select_subclass(self):
        subclasses = ["answer", "question"]
        for subclass in subclasses:
            try:
                return getattr(self, subclass)
            except ObjectDoesNotExist:
                pass
        return self

    def select_parent(self):
        if not self.__class__ is Content:
            return self.content_ptr
        else:
            return self


class Question(Content):
    content = models.CharField(_("question"), max_length=200)

    class Meta:
        verbose_name = _("question")

    def __unicode__(self):
        return truncatechars(self.content, 50)

    def save(self):
        super(Question, self).save()
        for answer in self.answer_set.all():
            answer.items = self.items.values_list("id", flat=True)
            answer.tags.set(*self.tags.all())

    def get_absolute_url(self):
        return reverse("item_detail", args=[self._meta.module_name, self.id,
                                            slugify(unicode(self))])

    def get_product_related_url(self, item):
        return CONTENT_URL_PATTERN % {
            "path": item.get_absolute_url(),
            "query_string": self.query_string, "anchor": self.anchor
        }

    def sort_related_answers(self, option="popular"):
        answer_qs = Content.objects.filter(answer__question=self)
        ids = [a._get_pk_val() for a in answer_qs.order_queryset(option)]
        self.set_answer_order(ids)


class Answer(Content):
    question = models.ForeignKey(Question, verbose_name=_("question"),
                                 null=True)
    content = models.CharField(_("content"), max_length=10000)

    class Meta:
        verbose_name = _("answer")
        order_with_respect_to = "question"

    def __unicode__(self):
        return truncatechars(strip_tags(self.content), 50)

    def save(self):
        super(Answer, self).save()
        self.items = self.question.items.values_list("id", flat=True)
        self.tags.set(*self.question.tags.all())

    def get_absolute_url(self):
        return CONTENT_URL_PATTERN % {
            "path": self.question.get_absolute_url(),
            "query_string": self.query_string, "anchor": self.anchor
        }

    def get_product_related_url(self, item):
        return CONTENT_URL_PATTERN % {
            "path": item.get_absolute_url(),
            "query_string": self.query_string, "anchor": self.anchor
        }

from content.transition import sync_products


class TopCategories(object):
    delta = timezone.now() - datetime.timedelta(days=4 * 31)
    queryset = Tag.objects.annotate(
        weight=Count('taggit_taggeditem_items')).order_by('-weight')

    def by_contributions(self):
        return self.queryset

    def top_products_for_category(self, category, n=6):
        kwargs = {"content__created__gt": self.delta}
        if isinstance(category, Tag):
            kwargs.update({"tags": category})
        else:
            kwargs.update({"tags__name": unicode(category)})
        qs = Item.objects.filter(**kwargs)
        if qs:
            qs = qs.order_queryset("popular")[:n].fetch_images()
        return qs

    def top_products_by_categories(self, categories=["all"], n=6):
        products = SortedDict()
        for cat in categories:
            products.update({cat: self.top_products_for_category(cat, n)})
        return products

    def categories_objects(self, cat):
        return map(lambda x: x.content_object,
                   Tag.objects.get(name=cat).taggit_taggeditem_items.all())

    def similars(self, cat1, cat2):
        s1, s2 = map(self.categories_objects, [cat1, cat2])
        i = 0
        for x in s2:
            if x in s1:
                i += 1
        return float(i) / len(s2)

    def compare(self, cat, cat_list, threshold=0):
        f = lambda x: x[1] > threshold
        return {cat: filter(f, [(c, self.similars(c, cat)) for c in cat_list])}

    def test_sub_categories(self, n=14):
        import pprint
        top = self.by_contributions()[:n]
        comp = OrderedDict()
        for i, t in enumerate(top):
            comp.update(TopCategories().compare(t, top[:i], .1))
        pprint.pprint(comp)
        return comp

    def sub_categories(self, n=14):
        comp = self.test_sub_categories(n)
        tc = self.by_contributions()[:n]
        cleancat = []
        for tag in comp:
            if tag in tc:
                is_sub = 0
                for sub in comp[tag]:
                    if sub[1] > 0.6:
                        print tag, "is a sub cat of", sub[0]
                        is_sub = 1
                if not is_sub:
                    cleancat.append(tag)
        return cleancat
