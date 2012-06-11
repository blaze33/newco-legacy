from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import pre_save, post_save, post_delete
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType

from idios.models import ProfileBase

from voting.models import Vote
from items.models import Question, Answer

import datetime


class Profile(ProfileBase):
    name = models.CharField(_("name"), max_length=50, null=True, blank=True)
    about = models.TextField(_("about"), null=True, blank=True)
    location = models.CharField(_("location"), max_length=40, null=True,
                                                              blank=True)
    website = models.URLField(_("website"), null=True, blank=True,
                                                       verify_exists=False)
    subscription_date = models.DateTimeField(default=datetime.datetime.today(),
                                    editable=False,
                                    verbose_name=_('subscription date'))


class Reputation(models.Model):
    user = models.OneToOneField(User)
    reputation_incremented = models.IntegerField(default=0)
    reputation_computed = models.IntegerField(default=0)

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
                rep += POINTSTABLE[cls._meta.module_name][vote.vote]

        return rep


def create_reputation(sender, instance=None, **kwargs):
    if instance is None:
        return
    rep, created = Reputation.objects.get_or_create(user=instance)
    rep.reputation_computed = rep.compute_reputation()
    rep.reputation_incremented = rep.reputation_computed
    rep.save()
post_save.connect(create_reputation, sender=User)


def decrement_reputation(sender, instance=None, **kwargs):
    if instance is None:
        return
    content = instance.object
    rep = Reputation.objects.get(user=content.author)
    rep.reputation_incremented -= instance.vote
    rep.save()
post_delete.connect(decrement_reputation, sender=Vote)


def amend_reputation(sender, instance=None, **kwargs):
    if instance is None:
        return
    content = instance.object

    try:
        vote = Vote.objects.get(pk=instance.pk)
        rep = Reputation.objects.get(user=content.author)
        rep.reputation_incremented -= vote.vote
        rep.save()
    except:
        pass

    rep = Reputation.objects.get(user=content.author)
    rep.reputation_incremented += instance.vote
    rep.save()
pre_save.connect(amend_reputation, sender=Vote)


def update_permissions(sender, instance=None, **kwargs):
    if instance is None:
        return

    content_type = ContentType.objects.get(app_label=Vote._meta.app_label,
                                           model=Vote._meta.module_name)
    permission, created = Permission.objects.get_or_create(codename='can_vote',
                                       name='Can vote on content',
                                       content_type=content_type)

    if instance.reputation_incremented >= 2:
        instance.user.user_permissions.add(permission)
    else:
        instance.user.user_permissions.remove(permission)
post_save.connect(update_permissions, sender=Reputation)
