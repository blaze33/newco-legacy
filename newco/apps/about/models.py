from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django_extensions.db.models import TimeStampedModel

# Create your models here.
class LastMail(TimeStampedModel):
    user = models.OneToOneField(User)