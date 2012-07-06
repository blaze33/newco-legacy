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


@register.inclusion_tag('items/_tag_edit.html')
def edit(item_name, item_id):
    return {
        'item_name': item_name,
        'item_id': item_id,
    }


@register.tag
def popover_link(parser, token):
    """
    Renders the item link with its popover.

    Usage::

        {% item_link object template %}

    """
    bits = token.split_contents()
    return PopoverLinkNode(*bits[1:])


class PopoverLinkNode(template.Node):
    def __init__(self, obj, tpl=None):
        self.obj = template.Variable(obj)
        self.template = tpl[1:-1] if tpl else None

    def render(self, context):
        obj = self.obj.resolve(context)
        if obj._meta.module_name == "item":
            tag_list = obj.tags.all()
            if not self.template:
                self.template = "items/_popover_link.html"
        elif obj._meta.module_name == "user":
            tag_list = obj.get_profile().skills.all()
            if not self.template:
                self.template = "profiles/_popover_link.html"

        ctx = {
            'object': self.obj.resolve(context),
            'tag_list': tag_list
        }
        return template.loader.render_to_string(self.template, ctx,
            context_instance=context)
