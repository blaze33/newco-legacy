from django.contrib import admin

from items.models import Item, Question, Answer, Story
from items.models import Link, Feature

import autocomplete_light
from items.models import Item

#admin.site.register(Item)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Story)
admin.site.register(Link)
admin.site.register(Feature)

class ItemAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(Item)

admin.site.register(Item,ItemAdmin)