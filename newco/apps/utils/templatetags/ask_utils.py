from django import template

register = template.Library()


@register.tag
def ask_form(parser, token):
    """
    Renders the ask form.

    Usage::

        {% ask_form object vote %}

    """
    bits = token.split_contents()
    return AskFormNode(*bits[1:])


class AskFormNode(template.Node):
    def __init__(self, obj, tpl=None):
        self.obj = template.Variable(obj)
        self.template = 'ask/form.html'

    def render(self, context):
        ctx = {
            'object': self.obj.resolve(context),
        }
        return template.loader.render_to_string(self.template, ctx,
            context_instance=context)
