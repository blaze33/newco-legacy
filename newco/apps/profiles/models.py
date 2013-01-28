import json

from django.core.urlresolvers import reverse
from django.dispatch import receiver
from django.db import models
from django.db.models.signals import pre_save, post_save, pre_delete
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType

from idios.models import ProfileBase
from follow.utils import register
from taggit.managers import TaggableManager

from items.models import Content
from profiles.settings import POINTS_TABLE_RATED, POINTS_TABLE_RATING
from utils.voting import Vote

register(User)


class ProfileManager(models.Manager):

    def get_all_names(self):
        qs = self.order_by("name").distinct("name")
        return json.dumps(filter(None, qs.values_list("name", flat=True)))


class Profile(ProfileBase):
    name = models.CharField(_("name"), max_length=30, null=True, blank=True)
    slug = models.SlugField(verbose_name=_('slug'), editable=False)
    about = models.TextField(_("about"), null=True, blank=True)
    location = models.CharField(_("location"), max_length=40, null=True,
                                blank=True)
    website = models.URLField(_("website"), null=True, blank=True,
                              verify_exists=False)
    skills = TaggableManager(
        blank=True, verbose_name=_("skills"),
        help_text=_("The list of your main product skills"),
    )

    objects = ProfileManager()

    class Meta:
        verbose_name = _("profile")
        ordering = ["name", ]

    def __unicode__(self):
        return self.name

    def save(self, **kwargs):
        self.slug = slugify(self.name)
        super(Profile, self).save(**kwargs)

    def get_absolute_url(self):
        kwargs = {'pk': self.pk, 'slug': self.slug}
        return reverse('profile_detail', kwargs=kwargs)

    def get_profile(self):
        return self


class Reputation(models.Model):
    user = models.OneToOneField(User)
    reputation_incremented = models.IntegerField(default=0)
    reputation_computed = models.IntegerField(default=0)

    class Meta:
        verbose_name = _("reputation")
        permissions = (
            ("can_vote", "Can vote on content"),
        )

    def __unicode__(self):
        return u'%s\'s reputation' % (self.user)

    def compute_reputation(self):
        rep = 0

        ctype = ContentType.objects.get_for_model(Content)
        obj_ids = Content.objects.filter(
            author=self.user).values_list('id', flat=True)
        votes = Vote.objects.filter(object_id__in=obj_ids,
                                    content_type=ctype)

        for vote in votes:
            module_name = vote.object.select_subclass()._meta.module_name
            rep += POINTS_TABLE_RATED[module_name][vote.vote]

        votes = Vote.objects.filter(user=self.user)
        for vote in votes:
            module_name = vote.object.select_subclass()._meta.module_name
            rep += POINTS_TABLE_RATING[module_name][vote.vote]

        return rep


@receiver(post_save, sender=User)
def create_reputation(sender, instance=None, raw=False, **kwargs):
    if instance is None or raw:
        return
    rep, created = Reputation.objects.get_or_create(user=instance)
    rep.reputation_computed = rep.compute_reputation()
    rep.reputation_incremented = rep.reputation_computed
    rep.save()


def increment_reputation(sender, instance=None, **kwargs):
    if instance is None:
        return
    vote = instance

    # Update reputation for owner of rated content
    try:
        rep_rated = Reputation.objects.get(user=vote.object.author)
        module_name = vote.object.select_subclass()._meta.module_name
        rep_rated.reputation_incremented += \
            POINTS_TABLE_RATED[module_name][vote.vote]
        rep_rated.save()
    except:
        pass

    # Update reputation for rater
    try:
        rep_rating = Reputation.objects.get(user=vote.user)
        module_name = vote.object.select_subclass()._meta.module_name
        rep_rating.reputation_incremented += \
            POINTS_TABLE_RATING[module_name][vote.vote]
        rep_rating.save()
    except:
        pass


@receiver(pre_delete, sender=Vote)
def decrement_reputation(sender, instance=None, **kwargs):
    if instance is None:
        return
    vote = instance

    # Update reputation for owner of rated content
    try:
        rep_rated = Reputation.objects.get(user=vote.object.author)
        module_name = vote.object.select_subclass()._meta.module_name
        rep_rated.reputation_incremented -= \
            POINTS_TABLE_RATED[module_name][vote.vote]
        rep_rated.save()
    except:
        pass

    # Update reputation for rater
    try:
        rep_rating = Reputation.objects.get(user=vote.user)
        module_name = vote.object.select_subclass()._meta.module_name
        rep_rating.reputation_incremented -= \
            POINTS_TABLE_RATING[module_name][vote.vote]
        rep_rating.save()
    except:
        pass


@receiver(pre_save, sender=Vote)
def amend_reputation(sender, instance=None, **kwargs):
    if instance is None:
        return

    try:
        vote = Vote.objects.get(pk=instance.pk)

        decrement_reputation(sender, vote)
    except:
        pass

    increment_reputation(sender, instance)


@receiver(post_save, sender=Reputation)
def update_permissions(sender, instance=None, **kwargs):
    if instance is None:
        return

    content_type = ContentType.objects.get_for_model(Reputation)
    permission = Permission.objects.get(codename='can_vote',
                                        content_type=content_type)
    instance.user.user_permissions.add(permission)

#    if instance.reputation_incremented >= 2:
#        instance.user.user_permissions.add(permission)
#    else:
#        instance.user.user_permissions.remove(permission)
