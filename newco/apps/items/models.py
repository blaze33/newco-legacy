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
    tags = TaggableManager()
    
    def save(self):
        self.slug = slugify(self.name)
        super(Item, self).save()

    class Meta:
             pass
    def __unicode__(self):
        return u'%s' % (self.name)
    
    @permalink
    def get_absolute_url(self):
            return ('item_detail', None, {"item_id": self.id,"slug": self.slug} )

class Question(models.Model):
    content = models.CharField(max_length=200)
    pub_date = models.DateTimeField(_('date published'))
    author = models.ForeignKey(User)
    items = models.ManyToManyField(Item)

class Answer(models.Model):
    question = models.ForeignKey(Question)
    content = models.CharField(max_length=1000)
    pub_date = models.DateTimeField(_('date published'))
    author = models.ForeignKey(User)

class Story(models.Model):
    title = models.CharField(max_length=200)
    content = models.CharField(max_length=2000)
    items = models.ManyToManyField(Item)


