from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from django.db.models import permalink
from django.template.defaultfilters import slugify
from django.contrib.contenttypes import generic
import datetime

from voting.models import Vote
from idios.models import ProfileBase


class CannotManage(Exception):
    pass


class Content(models.Model):

    author = models.ForeignKey(User, null=True)
    pub_date = models.DateTimeField(default=datetime.datetime.today(),
                                    editable=False,
                                    verbose_name=_('date published'))

    class Meta:
        abstract = True

    def user_can_manage_me(self, user):
        try:
            if user == self.author:
                return user == self.author or user.is_superuser
        except AttributeError:
            pass
        return user.is_superuser

    def delete(self):
        try:
            self.votes.all().delete()
        except:
            pass
        super(Content, self).delete()


class Item(Content):
    name = models.CharField(max_length=255, verbose_name=_('name'))
    slug = models.SlugField(verbose_name=_('slug'), editable=False)
    last_modified = models.DateTimeField(auto_now=True,
                                         verbose_name=_('last modified'))
    tags = TaggableManager(help_text=_("A comma-separated list of tags"))

    class Meta:
        verbose_name = _('item')

    def __unicode__(self):
        return u'%s' % (self.name)

    def compute_tags(self, list_users):
        li=[]
        for user in list_users:
            if user in self.tags.similar_objects():
                li.append(user)
        return li
 
    def save(self):
        self.slug = slugify(self.name)
        super(Item, self).save()

    @permalink
    def get_absolute_url(self):
        return ('item_detail', None, {"model_name": "item",
                                      "pk": self.id,
                                      "slug": self.slug})


class Question(Content):
    content = models.CharField(max_length=200, verbose_name=_('content'))
    items = models.ManyToManyField(Item)
    votes = generic.GenericRelation(Vote)

    class Meta:
        verbose_name = _('question')
        ordering = ["-pub_date"]

    def __unicode__(self):
        return u'%s' % (self.content)

    @permalink
    def get_absolute_url(self):
        return ('item_detail', None, {"model_name": "item",
                                      "pk": self.items.all()[0].id,
                                      "slug": self.items.all()[0].slug})


class Answer(Content):
    question = models.ForeignKey(Question, null=True)
    content = models.CharField(max_length=1000, verbose_name=_('content'))
    votes = generic.GenericRelation(Vote)

    class Meta:
        verbose_name = _('answer')

    def __unicode__(self):
        return u'Answer %s on %s' % (self.id, self.question)

    @permalink
    def get_absolute_url(self):
        item = self.question.items.all()[0]
        return ('item_detail', None, {"model_name": "item",
                                      "pk": item.id,
                                      "slug": item.slug})


class Story(models.Model):
    title = models.CharField(max_length=200)
    content = models.CharField(max_length=2000)
    items = models.ManyToManyField(Item)
    votes = generic.GenericRelation(Vote)


class ExternalLink(Content):
    text = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    items = models.ManyToManyField(Item)
    votes = generic.GenericRelation(Vote)

    def __unicode__(self):
        return u'%s' % (self.text)
    
    @permalink
    def get_absolute_url(self):
        return ('item_detail', None, {"model_name": "item",
                                      "pk": self.items.all()[0].id,
                                      "slug": self.items.all()[0].slug})
        
class FeatureP(Content):
    content = models.CharField(max_length=80)
    items = models.ManyToManyField(Item)
    votes = generic.GenericRelation(Vote)

    def __unicode__(self):
        return u'%s' % (self.content)

    @permalink
    def get_absolute_url(self):
        return ('item_detail', None, {"model_name": "item",
                                      "pk": self.items.all()[0].id,
                                      "slug": self.items.all()[0].slug})
 
class FeatureN(Content):
    content = models.CharField(max_length=80)
    items = models.ManyToManyField(Item)
    votes = generic.GenericRelation(Vote)

    def __unicode__(self):
        return u'%s' % (self.content)

    @permalink
    def get_absolute_url(self):
        return ('item_detail', None, {"model_name": "item",
                                      "pk": self.items.all()[0].id,
                                      "slug": self.items.all()[0].slug})
 