from django.contrib import admin

from items.models import Item, Question, Answer, Story

admin.site.register(Item)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Story)
