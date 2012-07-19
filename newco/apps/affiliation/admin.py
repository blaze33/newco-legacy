from django.contrib import admin

from affiliation.models import Currency, Store, AffiliationItem

admin.site.register(Currency)
admin.site.register(Store)
admin.site.register(AffiliationItem)
