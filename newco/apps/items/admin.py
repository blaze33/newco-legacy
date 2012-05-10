from items.models import *
from django.contrib import admin

class ItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Item, ItemAdmin)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Story)
