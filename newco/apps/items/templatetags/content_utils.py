from django import template

register = template.Library()

@register.filter
def to_class_name(value):
    return value.__class__.__name__

@register.inclusion_tag('items/tag_edit.html')
def edit(item_name, item_id):
    return {'item_name': item_name,
            'item_id': item_id,
            }
