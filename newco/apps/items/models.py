from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import permalink
from django.template.defaultfilters import slugify, truncatechars
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User
from django.contrib.contenttypes import generic

from follow.utils import register
from model_utils import Choices
from model_utils.managers import QueryManager
from taggit_autosuggest.managers import TaggableManager
from voting.models import Vote

from items.managers import ContentManager


class Item(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("name"))
    slug = models.SlugField(verbose_name=_("slug"), editable=False)
    author = models.ForeignKey(User, null=True)
    pub_date = models.DateTimeField(default=timezone.now, editable=False,
                                    verbose_name=_('date published'))
    last_modified = models.DateTimeField(auto_now=True,
                                         verbose_name=_("last modified"))
    tags = TaggableManager()

    class Meta:
        verbose_name = _("product")

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

    def node(self):
        return sync_products(Item, self)
register(Item)


class Content(models.Model):
    STATUS = Choices(
        (0, "draft", _("Draft")),
#        (1, "sandbox", _("Sandbox")),
        (2, "public", _("Public"))
    )

    author = models.ForeignKey(User, null=True)
    pub_date = models.DateTimeField(default=timezone.now, editable=False,
                                    verbose_name=_("date published"))
    status = models.SmallIntegerField(choices=STATUS, default=STATUS.public,
                                      verbose_name=_("status"))
    items = models.ManyToManyField(Item, verbose_name=_("products"))
    votes = generic.GenericRelation(Vote)

    public = QueryManager(status=STATUS.public)

    objects = ContentManager()

    class Meta:
        ordering = ["-pub_date"]

    def save(self):
        super(Content, self).save()
        obj = self.select_parent()
        if obj.votes.count() == 0:
            user1 = User.objects.get(id=2)
            Vote.objects.record_vote(obj, user1, 0)

    def delete(self):
        try:
            self.votes.all().delete()
        except:
            pass
        super(Content, self).delete()

    def is_public(self):
        return self.status == self.STATUS.public

    def is_draft(self):
        return self.status == self.STATUS.draft

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
    content = models.CharField(max_length=200, verbose_name=_("content"))

    class Meta:
        verbose_name = _("question")

    def __unicode__(self):
        return truncatechars(self.content, 50)

    @permalink
    def get_absolute_url(self):
        return ("item_detail", [], {"model_name": self._meta.module_name,
                                    "pk": self.id,
                                    "slug": slugify(unicode(self))})

    def get_product_related_url(self, item,
                                anchor_pattern="?question=%(id)s#q-%(id)s"):
        return item.get_absolute_url() + (anchor_pattern % self.__dict__)


class Answer(Content):
    question = models.ForeignKey(Question, null=True)
    content = models.CharField(max_length=1000, verbose_name=_("content"))

    class Meta:
        verbose_name = _("answer")

    def __unicode__(self):
        return truncatechars(self.content, 50)

    def get_absolute_url(self, anchor_pattern="?answer=%(id)s#a-%(id)s"):
        return self.question.get_absolute_url() + \
            (anchor_pattern % self.__dict__)

    def get_product_related_url(self, item,
                                anchor_pattern="?answer=%(id)s#a-%(id)s"):
        return item.get_absolute_url() + (anchor_pattern % self.__dict__)


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
