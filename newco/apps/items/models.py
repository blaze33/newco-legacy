from django.db import models
from django.utils.translation import ugettext_lazy as _
from taggit.managers import TaggableManager

class Question(models.Model):
    content = models.CharField(max_length=200)
    pub_date = models.DateTimeField(_('date published'))

class Answer(models.Model):
    question = models.ForeignKey(Question)
    content = models.CharField(max_length=1000)

class Story(models.Model):
    title = models.CharField(max_length=200)
    content = models.CharField(max_length=2000)

class Item(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    slug = models.SlugField(verbose_name=_('Slug'), unique=True)
    last_modified = models.DateTimeField(auto_now=True,
        verbose_name=_('Last modified'))
    tags = TaggableManager()
    questions = models.ManyToManyField(Question)
    stories = models.ManyToManyField(Story)
