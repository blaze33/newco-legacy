from django import template

register = template.Library()


@register.tag
def vote_form(parser, token):
    """
    Renders the vote form.

    Usage::

        {% vote_form object vote %}

    """
    bits = token.split_contents()
    return VoteFormNode(*bits[1:])


class VoteFormNode(template.Node):
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
