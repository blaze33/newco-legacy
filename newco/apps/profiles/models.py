from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.contrib.auth.models import User

from idios.models import ProfileBase

from voting.models import Vote

import datetime


class Profile(ProfileBase):
    name = models.CharField(_("name"), max_length=50, null=True, blank=True)
    about = models.TextField(_("about"), null=True, blank=True)
    location = models.CharField(_("location"), max_length=40, null=True, blank=True)
    website = models.URLField(_("website"), null=True, blank=True, verify_exists=False)
    subscription_date = models.DateTimeField(default=datetime.datetime.today(),
                                    editable=False,
                                    verbose_name=_('date published'))


class Reputation(models.Model):
    user = models.OneToOneField(User)
    reputation_value = models.IntegerField(default=0)
    
    
def create_reputation(sender, instance=None, **kwargs):
    if instance is None:
        return
    reputation, created = Reputation.objects.get_or_create(user=instance)
post_save.connect(create_reputation, sender=User)


def increment_reputation(sender, instance=None, **kwargs):
    if instance is None:
        return
    obj = instance.object
    reputation = Reputation.objects.get(user=obj.author)
    reputation.reputation_value += instance.vote
    reputation.save()
post_save.connect(increment_reputation, sender=Vote)