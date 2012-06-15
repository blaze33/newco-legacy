from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from taggit.managers import TaggableManager

from idios.models import ProfileBase

from voting.models import Vote
from items.models import Question, Answer
from profiles.settings import POINTS_TABLE_RATED, POINTS_TABLE_RATING


from follow import utils



class Profile(ProfileBase):
    name = models.CharField(_("name"), max_length=50, null=True, blank=True)
    about = models.TextField(_("about"), null=True, blank=True)
    location = models.CharField(_("location"), max_length=40, null=True,
                                                              blank=True)
    website = models.URLField(_("website"), null=True, blank=True,
                                                       verify_exists=False)
    skills = TaggableManager(help_text="The list of your main product skills")


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

        for cls in [Question, Answer]:
            ctype = ContentType.objects.get(
                                    app_label=cls._meta.app_label,
                                    model=cls._meta.module_name
                    )
            queryset = cls.objects.filter(author=self.user)
            obj_ids = [q._get_pk_val() for q in queryset]
            votes = Vote.objects.filter(object_id__in=obj_ids,
                                        content_type=ctype)

            for vote in votes:
                rep += POINTS_TABLE_RATED[cls._meta.module_name][vote.vote]

        votes = Vote.objects.filter(user=self.user)
        for vote in votes:
            rep += POINTS_TABLE_RATING[vote.content_type.name][vote.vote]

        return rep


@receiver(post_save, sender=User)
def create_reputation(sender, instance=None, **kwargs):
    if instance is None:
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
        rep_rated.reputation_incremented += \
                POINTS_TABLE_RATED[vote.content_type.name][vote.vote]
        rep_rated.save()
    except:
        pass

    # Update reputation for rater
    try:
        rep_rating = Reputation.objects.get(user=vote.user)
        rep_rating.reputation_incremented += \
                POINTS_TABLE_RATING[vote.content_type.name][vote.vote]
        rep_rating.save()
    except:
        pass


@receiver(post_delete, sender=Vote)
def decrement_reputation(sender, instance=None, **kwargs):
    if instance is None:
        return
    vote = instance

    # Update reputation for owner of rated content
    try:
        rep_rated = Reputation.objects.get(user=vote.object.author)
        rep_rated.reputation_incremented -= \
                POINTS_TABLE_RATED[vote.content_type.name][vote.vote]
        rep_rated.save()
    except:
        pass

    # Update reputation for rater
    try:
        rep_rating = Reputation.objects.get(user=vote.user)
        rep_rating.reputation_incremented -= \
                POINTS_TABLE_RATING[vote.content_type.name][vote.vote]
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

    content_type = ContentType.objects.get(app_label=Reputation._meta.app_label,
                                           model=Reputation._meta.module_name)
    permission = Permission.objects.get(codename='can_vote',
                                       content_type=content_type)
    instance.user.user_permissions.add(permission)

#    if instance.reputation_incremented >= 2:
#        instance.user.user_permissions.add(permission)
#    else:
#        instance.user.user_permissions.remove(permission)

utils.register(User)
