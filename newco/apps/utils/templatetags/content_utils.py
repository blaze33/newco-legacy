from django import template
from gravatar.templatetags.gravatar import gravatar_img_for_user

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

@register.simple_tag
def profile_pic(user, size=None):
    """
    Returns the user profile picture. Only supports gravatar for now.

    Syntax::

        {% profile_pic_for_user <user> [size] %}

    Example::

        {% profile_pic_for_user request.user 48 %}
        {% profile_pic_for_user 'max' 48 %}
    """
    return gravatar_img_for_user(user, size, rating=None)
