# coding: utf-8
from django.conf import settings
print "Using " + settings.DATABASES["default"]["NAME"] + """ database.
Items having a class property will have it renamed to _class
"""
from content.models import Item

for klass, kount in Item.objects.hvalues('class'):
    Item.objects.hfilter({'class':klass}).hupdate('data', {'_class':klass})
    Item.objects.hfilter({'class':klass}).hremove('data', 'class')
