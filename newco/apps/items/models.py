from django.db import models
from django.db.models import permalink, Q
from django.template.defaultfilters import slugify, truncatechars
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User
from django.contrib.contenttypes import generic

from model_utils import Choices
from model_utils.managers import InheritanceManager, QueryManager
from follow.models import Follow
from follow.utils import register
from taggit_autosuggest.managers import TaggableManager
from voting.models import Vote


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
        return ("item_detail", None, {"model_name": self._meta.module_name,
                                      "pk": self.id,
                                      "slug": self.slug})

    def node(self):
        return sync_products(Item, self)
register(Item)


class ContentManager(InheritanceManager):
    def get_feed(self, user):
        """
        Get the newsfeed of a specific user
        """
        obj_fwed = Follow.objects.filter(user=user)
        fwees_ids = obj_fwed.values_list('target_user_id', flat=True)
        items_fwed_ids = obj_fwed.values_list('target_item_id', flat=True)

        return self.filter(
                Q(author__in=fwees_ids) | Q(items__in=items_fwed_ids),
                ~Q(author=user), status=Content.STATUS.public
        )

    def get_related_contributions(self, user):
        profile = user.get_profile()
        item_list = Item.objects.filter(tags__in=profile.skills.all())
        return self.filter(items__in=item_list)


class Content(models.Model):
    STATUS = Choices(
        (0, "draft", _("Draft")),
#        (1, "sandbox", _("Sandbox")),
        (2, "public", _("Public"))
    )

    author = models.ForeignKey(User, null=True)
    pub_date = models.DateTimeField(default=timezone.now, editable=False,
                                            verbose_name=_('date published'))
    status = models.SmallIntegerField(choices=STATUS, default=STATUS.public,
                                            verbose_name=_('status'))
    items = models.ManyToManyField(Item)

    public = QueryManager(status=STATUS.public)

    objects = ContentManager()

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
    votes = generic.GenericRelation(Vote)

    class Meta:
        verbose_name = _("question")

    def __unicode__(self):
        return truncatechars(self.content, 50)

    @permalink
    def get_absolute_url(self):
        return ("item_detail", None, {"model_name": self._meta.module_name,
                        "pk": self.id, "slug": slugify(self.__unicode__())})

    def get_product_related_url(self, item,
                                anchor_pattern="/question-%(id)s#q-%(id)s"):
        return item.get_absolute_url() + (anchor_pattern % self.__dict__)


class Answer(Content):
    question = models.ForeignKey(Question, null=True)
    content = models.CharField(max_length=1000, verbose_name=_("content"))
    votes = generic.GenericRelation(Vote)

    class Meta:
        verbose_name = _("answer")

    def __unicode__(self):
        return truncatechars(self.content, 50)

    def get_absolute_url(self, anchor_pattern="/answer-%(id)s#a-%(id)s"):
        return self.question.get_absolute_url() + \
                                            (anchor_pattern % self.__dict__)

    def get_product_related_url(self, item,
                                anchor_pattern="/answer-%(id)s#a-%(id)s"):
        return item.get_absolute_url() + (anchor_pattern % self.__dict__)


class Link(Content):
    content = models.CharField(max_length=200, verbose_name=_("content"))
    url = models.URLField(max_length=200, verbose_name=_("URL"))
    votes = generic.GenericRelation(Vote)

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
    votes = generic.GenericRelation(Vote)

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

from content.transition import sync_products
