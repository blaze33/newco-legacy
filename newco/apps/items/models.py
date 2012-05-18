from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from django.db.models import permalink
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse


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


class Question(models.Model):
    content = models.CharField(max_length=200, verbose_name=_('Ask a question'))
    pub_date = models.DateTimeField(auto_now=True,
                    verbose_name=_('Date published'))
    user = models.ForeignKey(User, null=True, blank=True, default=None,
                    verbose_name=_("User"), editable=False)
    item = models.ForeignKey(Item, null=True, blank=True, default=None,
                    verbose_name=_("Item"), editable=False)

    objects = models.Manager()

    def __unicode__(self):
        return u'%s' % (self.content)

    @permalink
    def get_absolute_url(self):
        return ('item_detail', None, {"item_id": self.item.id, "slug": self.item.slug})


class Answer(models.Model):
    question = models.ForeignKey(Question)
    content = models.CharField(max_length=1000)
    pub_date = models.DateTimeField(auto_now=True,
                    verbose_name=_('Date published'))
    user = models.ForeignKey(User, null=True, blank=True, default=None,
                    verbose_name=_("User"), editable=False)


class Story(models.Model):
    title = models.CharField(max_length=200)
    content = models.CharField(max_length=2000)
    items = models.ManyToManyField(Item)
