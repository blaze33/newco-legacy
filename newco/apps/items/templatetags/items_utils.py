from django import template

register = template.Library()



@register.tag
def item_link(parser, token):
    """
    Renders the item link with its popover.

    Usage::

        {% item_link object xxx %}

    """
    bits = token.split_contents()
    return ItemLinkNode(*bits[1:])


class ItemLinkNode(template.Node):
    def __init__(self, obj):
        self.obj = template.Variable(obj)
        ##self.xxx = template.Variable(xxx)
        self.template = 'items/item_link.html'

    def render(self, context):
        ctx = {
            'object': self.obj.resolve(context),
            ##'xxx': self.xxx.resolve(context)
        }
        return template.loader.render_to_string(self.template, ctx,
            context_instance=context)
