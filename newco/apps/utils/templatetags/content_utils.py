from django import template

register = template.Library()


@register.filter
def to_app_label(value):
    return value._meta.app_label


@register.filter
def to_class_name(value):
    return value._meta.module_name


@register.filter
def verbose_name(value):
    return value._meta.verbose_name


@register.filter
def get_at_index(list, index):
    return list[index]


@register.inclusion_tag('items/tag_edit.html')
def edit(item_name, item_id):
    return {
        'item_name': item_name,
        'item_id': item_id,
    }
