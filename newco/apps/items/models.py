from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from taggit_autosuggest.managers import TaggableManager
from django.db.models import permalink
from django.template.defaultfilters import slugify
from django.contrib.contenttypes import generic
from datetime import datetime

from voting.models import Vote
from follow.utils import register



class Status(models.Model):
    name = models.CharField(max_length=25, verbose_name=_("status name"))
    
    class Meta:
        verbose_name = _("Status")
        verbose_name_plural = _("Statuses")

    def __unicode__(self):
        return u"%s" % (self.name)


class Content(models.Model):
    author = models.ForeignKey(User, null=True)
    pub_date = models.DateTimeField(default=datetime.now, editable=False,
                                            verbose_name=_('date published'))
    status = models.ForeignKey(Status, null=True)

    class Meta:
        abstract = True

    def delete(self):
        try:
            self.votes.all().delete()
        except:
            pass
        super(Content, self).delete()


class Item(Content):
    name = models.CharField(max_length=255, verbose_name=_("name"))
    slug = models.SlugField(verbose_name=_("slug"), editable=False)
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


class Question(Content):
    content = models.CharField(max_length=200, verbose_name=_("content"))
    items = models.ManyToManyField(Item)
    votes = generic.GenericRelation(Vote)

    class Meta:
        verbose_name = _("question")
        ordering = ["-pub_date"]

    def __unicode__(self):
        q = self.content
        return u"%s" % (q if len(q) <= 50 else q[:50] + "...")

    def get_absolute_url(self, anchor_pattern="/question-%(id)s#q-%(id)s"):
        item = self.items.select_related()[0]
        return item.get_absolute_url() + (anchor_pattern % self.__dict__)


class Answer(Content):
    question = models.ForeignKey(Question, null=True)
    content = models.CharField(max_length=1000, verbose_name=_("content"))
    votes = generic.GenericRelation(Vote)

    class Meta:
        verbose_name = _("answer")

    def __unicode__(self):
        a = self.content
        return u"%s" % (a if len(a) <= 50 else a[:50] + "...")

    def get_absolute_url(self, anchor_pattern="/answer-%(id)s#a-%(id)s"):
        item = self.question.items.select_related()[0]
        return item.get_absolute_url() + (anchor_pattern % self.__dict__)


class Story(models.Model):
    title = models.CharField(max_length=200, verbose_name=_("title"))
    content = models.CharField(max_length=2000, verbose_name=_("content"))
    items = models.ManyToManyField(Item)
    votes = generic.GenericRelation(Vote)

    class Meta:
        verbose_name = _("story")
        verbose_name_plural = _("stories")


class ExternalLink(Content):
    content = models.CharField(max_length=200, verbose_name=_("content"))
    url = models.URLField(max_length=200, verbose_name=_("URL"))
    items = models.ManyToManyField(Item)
    votes = generic.GenericRelation(Vote)

    class Meta:
        verbose_name = _("link")
        ordering = ["-pub_date"]

    def __unicode__(self):
        return u"%s" % (self.content)

    def get_absolute_url(self, anchor_pattern="/link-%(id)s#l-%(id)s"):
        item = self.items.select_related()[0]
        return item.get_absolute_url() + (anchor_pattern % self.__dict__)


class Feature(Content):
    content = models.CharField(max_length=80, verbose_name=_('content'))
    positive = models.BooleanField()
    items = models.ManyToManyField(Item)
    votes = generic.GenericRelation(Vote)

    class Meta:
        verbose_name = _('feature')
        ordering = ["-pub_date"]

    def __unicode__(self):
        return u'%s' % (self.content)

    def get_absolute_url(self, anchor_pattern="/feature-%(id)s#f-%(id)s"):
        item = self.items.select_related()[0]
        return item.get_absolute_url() + (anchor_pattern % self.__dict__)
