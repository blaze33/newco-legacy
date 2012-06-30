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


@register.inclusion_tag('items/tag_edit.html')
def edit(item_name, item_id):
    return {
        'item_name': item_name,
        'item_id': item_id,
    }


@register.tag
def voting_form(parser, token):
    """
    Renders the voting form.

    Usage::

        {% voting_form object vote %}

    """
    bits = token.split_contents()
    return VotingFormNode(*bits[1:])


class VotingFormNode(template.Node):
    def __init__(self, obj, vote):
        self.obj = template.Variable(obj)
        self.vote = template.Variable(vote)
        self.template = 'voting/form.html'

    def render(self, context):
        ctx = {
            'object': self.obj.resolve(context),
            'vote': self.vote.resolve(context)
        }
        return template.loader.render_to_string(self.template, ctx,
            context_instance=context)
