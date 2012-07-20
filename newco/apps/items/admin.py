from django.contrib import admin

from items.models import Item, Question, Answer, Story
from items.models import Link, Feature, Attribute, Measure

admin.site.register(Item)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Story)
admin.site.register(Link)
admin.site.register(Feature)
admin.site.register(Attribute)
admin.site.register(Measure)
