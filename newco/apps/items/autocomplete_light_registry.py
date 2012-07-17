import autocomplete_light

from items.models import Item

autocomplete_light.register(Item, search_fields=('name',),
    autocomplete_js_attributes={'placeholder': 'item name ..'})