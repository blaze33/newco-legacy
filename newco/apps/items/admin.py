from django.contrib import admin

from items.models import Status, Item, Question, Answer, Story
from items.models import ExternalLink, Feature

admin.site.register(Status)
admin.site.register(Item)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Story)
admin.site.register(ExternalLink)
admin.site.register(Feature)
