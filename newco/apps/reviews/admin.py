# django imports
from django.contrib import admin

# lfs imports
from reviews.models import Review

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('content', 'user', 'score', 'creation_date', 'ip_address')
    list_filter = ('score', 'creation_date', 'user')
    search_fields = ('user',)#, 'ip_address',)

admin.site.register(Review, ReviewAdmin)