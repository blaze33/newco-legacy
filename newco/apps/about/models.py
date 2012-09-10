from django.db import models
from django.contrib.auth.models import User
from django_extensions.db.models import TimeStampedModel


class LastMail(TimeStampedModel):
    user = models.OneToOneField(User)

    class Meta:
        abstract = True
