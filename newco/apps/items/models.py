from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import permalink
from django.template.defaultfilters import slugify, truncatechars
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User
from django.contrib.contenttypes import generic

from follow.utils import register
from taggit.managers import TaggableManager
from voting.models import Vote

from items import QUERY_STR_PATTERNS, ANCHOR_PATTERNS, STATUSES
from items.managers import ContentManager, ItemManager

CONTENT_URL_PATTERN = "%(path)s?%(query_string)s#%(anchor)s"
TAG_VERBOSE_NAME = _("Tags")
TAG_HELP_TEXT = _("Add one or several related categories/activities using"
                  " Tab or Enter, and the Arrow keys.")


class Item(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("name"))
    slug = models.SlugField(verbose_name=_("slug"), editable=False)
    author = models.ForeignKey(User, null=True)
    pub_date = models.DateTimeField(default=timezone.now, editable=False,
                                    verbose_name=_('date published'))
    last_modified = models.DateTimeField(auto_now=True,
                                         verbose_name=_("last modified"))
    tags = TaggableManager(verbose_name=TAG_VERBOSE_NAME,
                           help_text=TAG_HELP_TEXT)

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
        maxl = self._meta.get_field_by_name('slug')[0].max_length
        self.slug = truncatechars(slugify(self.name), maxl)
        super(Item, self).save()

    @permalink
    def get_absolute_url(self):
        return ("item_detail", None, {"model_name": self._meta.module_name,
                                      "pk": self.id,
                                      "slug": self.slug})

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


class Content(models.Model):
    author = models.ForeignKey(User, null=True)
    pub_date = models.DateTimeField(default=timezone.now, editable=False,
                                    verbose_name=_("date published"))
    status = models.SmallIntegerField(
        choices=STATUSES, default=STATUSES.public, verbose_name=_("status"))
    items = models.ManyToManyField(Item, verbose_name=_("products"),
                                   blank=True)
    votes = generic.GenericRelation(Vote)
    tags = TaggableManager(blank=True, verbose_name=TAG_VERBOSE_NAME,
                           help_text=TAG_HELP_TEXT)

    objects = ContentManager()

    class Meta:
        ordering = ["-pub_date"]

    def delete(self):
        try:
            self.votes.all().delete()
        except:
            pass
        super(Content, self).delete()

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
        subclasses = ["answer", "question", "feature", "link"]
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
    content = models.CharField(max_length=200, verbose_name=_("question"))

    class Meta:
        verbose_name = _("question")

    def __unicode__(self):
        return truncatechars(self.content, 50)

    def save(self):
        super(Question, self).save()
        for answer in self.answer_set.all():
            answer.items = self.items.values_list("id", flat=True)
            answer.tags.set(*self.tags.all())

    @permalink
    def get_absolute_url(self):
        return ("item_detail", [], {"model_name": self._meta.module_name,
                                    "pk": self.id,
                                    "slug": slugify(unicode(self))})

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
    question = models.ForeignKey(Question, null=True)
    content = models.CharField(max_length=10000, verbose_name=_("content"))

    class Meta:
        verbose_name = _("answer")
        order_with_respect_to = "question"

    def __unicode__(self):
        return truncatechars(self.content, 50)

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


class Link(Content):
    content = models.CharField(max_length=200, verbose_name=_("content"))
    url = models.URLField(max_length=200, verbose_name=_("URL"))

    class Meta:
        verbose_name = _("link")

    def __unicode__(self):
        return u"%s" % (self.content)

    def get_absolute_url(self, anchor_pattern="?link=%(id)s#l-%(id)s"):
        item = self.items.select_related()[0]
        return item.get_absolute_url() + (anchor_pattern % self.__dict__)


class Feature(Content):
    content = models.CharField(max_length=80, verbose_name=_('content'))
    positive = models.BooleanField()

    class Meta:
        verbose_name = _('feature')

    def __unicode__(self):
        return u'%s' % (self.content)

    def get_absolute_url(self, anchor_pattern="?feature=%(id)s#f-%(id)s"):
        item = self.items.select_related()[0]
        return item.get_absolute_url() + (anchor_pattern % self.__dict__)


class Story(models.Model):
    title = models.CharField(max_length=200, verbose_name=_("title"))
    content = models.CharField(max_length=2000, verbose_name=_("content"))
    items = models.ManyToManyField(Item)
    votes = generic.GenericRelation(Vote)

    class Meta:
        verbose_name = _("story")
        verbose_name_plural = _("stories")

from content.transition import sync_products
