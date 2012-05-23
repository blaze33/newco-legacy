from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from django.db.models import permalink
from django.template.defaultfilters import slugify


class Item(models.Model):

    name = models.CharField(max_length=255, verbose_name=_('Name'))
    slug = models.SlugField(verbose_name=_('Slug'), editable=False)
    last_modified = models.DateTimeField(auto_now=True,
                    verbose_name=_('Last modified'))
    user = models.ForeignKey(User, null=True, blank=True, default=None,
                    verbose_name=_("User"), editable=False)
    tags = TaggableManager()

    objects = models.Manager()

    class Meta:
        pass

    def __unicode__(self):
        return u'%s' % (self.name)

    def save(self):
        self.slug = slugify(self.name)
        super(Item, self).save()

    @permalink
    def get_absolute_url(self):
        return ('item_detail', None, {"item_id": self.id, "slug": self.slug})


class Content(models.Model):
    pub_date = models.DateTimeField(auto_now=True,
                    verbose_name=_('Date published'))
    user = models.ForeignKey(User, null=True, blank=True, default=None,
                    verbose_name=_("User"), editable=False)

    objects = models.Manager()


class Question(Content):
    content = models.CharField(max_length=200,
                    verbose_name=_('Ask a question'))
    item = models.ForeignKey(Item, null=True, blank=True, default=None,
                    verbose_name=_("Item"), editable=False)

    def __unicode__(self):
        return u'%s' % (self.content)

    @permalink
    def get_absolute_url(self):
        return ('item_detail', None,
                {"item_id": self.item.id, "slug": self.item.slug})


class Answer(Content):
    content = models.CharField(max_length=1000,
                    verbose_name=_('Suggest an answer'))
    question = models.ForeignKey(Question, null=True, blank=True, default=None,
                    verbose_name=_("Question"), editable=False)

    def __unicode__(self):
        return u'%s' % (self.content)

    @permalink
    def get_absolute_url(self):
        item = self.question.item
        return ('item_detail', None,
                {"item_id": item.id, "slug": item.slug})


class Story(Content):
    title = models.CharField(max_length=200)
    content = models.CharField(max_length=2000)
    item = models.ForeignKey(Item, null=True, blank=True, default=None,
                    verbose_name=_("Item"), editable=False)

    class Meta:
        verbose_name_plural = "stories"

    def __unicode__(self):
        return u'%s' % (self.title)

    @permalink
    def get_absolute_url(self):
        return ('item_detail', None,
                {"item_id": self.item.id, "slug": self.item.slug})
