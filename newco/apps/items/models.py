from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from taggit_autosuggest.managers import TaggableManager
from django.db.models import permalink
from django.template.defaultfilters import slugify
from django.contrib.contenttypes import generic
from django.utils import timezone

from model_utils import Choices
from model_utils.managers import InheritanceManager, QueryManager
from voting.models import Vote
from follow.utils import register


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
        verbose_name = _("item")

    def __unicode__(self):
        return u"%s" % (self.name)

    def save(self):
        self.slug = slugify(self.name)
        super(Item, self).save()

    @permalink
    def get_absolute_url(self):
        return ('item_detail', None, {"model_name": "item",
                                      "pk": self.id,
                                      "slug": self.slug})
register(Item)


class Content(models.Model):
    STATUS = Choices(
        (0, "draft", _("Draft")),
#        (1, "sandbox", _("Sandbox")),
        (2, "public", _("Public"))
    )

    author = models.ForeignKey(User, null=True)
    pub_date = models.DateTimeField(default=timezone.now, editable=False,
                                            verbose_name=_('date published'))
    status = models.SmallIntegerField(choices=STATUS, default=STATUS.public)
    items = models.ManyToManyField(Item)
    votes = generic.GenericRelation(Vote)

    public = QueryManager(status=STATUS.public)

    objects = InheritanceManager()

    class Meta:
        ordering = ["-pub_date"]

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


class Question(Content):
    content = models.CharField(max_length=200, verbose_name=_("content"))

    class Meta:
        verbose_name = _("question")

    def __unicode__(self):
        q = self.content
        return u"%s" % (q if len(q) <= 50 else q[:50] + "...")

    def get_absolute_url(self, anchor_pattern="/question-%(id)s#q-%(id)s"):
        item = self.items.select_related()[0]
        return item.get_absolute_url() + (anchor_pattern % self.__dict__)


class Answer(Content):
    question = models.ForeignKey(Question, null=True)
    content = models.CharField(max_length=1000, verbose_name=_("content"))

    class Meta:
        verbose_name = _("answer")

    def __unicode__(self):
        a = self.content
        return u"%s" % (a if len(a) <= 50 else a[:50] + "...")

    def get_absolute_url(self, anchor_pattern="/answer-%(id)s#a-%(id)s"):
        item = self.question.items.select_related()[0]
        return item.get_absolute_url() + (anchor_pattern % self.__dict__)


class Link(Content):
    content = models.CharField(max_length=200, verbose_name=_("content"))
    url = models.URLField(max_length=200, verbose_name=_("URL"))

    class Meta:
        verbose_name = _("link")

    def __unicode__(self):
        return u"%s" % (self.content)

    def get_absolute_url(self, anchor_pattern="/link-%(id)s#l-%(id)s"):
        item = self.items.select_related()[0]
        return item.get_absolute_url() + (anchor_pattern % self.__dict__)


class Feature(Content):
    content = models.CharField(max_length=80, verbose_name=_('content'))
    positive = models.BooleanField()

    class Meta:
        verbose_name = _('feature')

    def __unicode__(self):
        return u'%s' % (self.content)

    def get_absolute_url(self, anchor_pattern="/feature-%(id)s#f-%(id)s"):
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
