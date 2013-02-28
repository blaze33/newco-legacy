# coding: utf-8
from django.conf import settings
print "Using " + settings.DATABASES["default"]["NAME"] + """ database.
TaggedItem referencing inexistent objects are deleted.
"""
from taggit.models import TaggedItem
from django.contrib.contenttypes.models import ContentType


def has_partner(t):
    return ContentType.objects.get_for_id(
        t.content_type_id).model_class()._default_manager.filter(
        id=t.object_id)

for potential_orphan in TaggedItem.objects.all():
    if not has_partner(potential_orphan):
        print potential_orphan
        potential_orphan.delete()
