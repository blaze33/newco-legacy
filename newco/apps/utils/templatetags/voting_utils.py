from django import template

register = template.Library()


@register.tag
def vote_form(parser, token):
    """
    Renders the vote form.

    Usage ('next' is not mandatory)::

        {% vote_form object vote next %}

    """
    bits = token.split_contents()
    obj = bits[1]
    vote = bits[2]
    if len(bits) == 4:
        next = parser.compile_filter(bits[3])
    else:
        next = None
    return VoteFormNode(obj, vote, next)


class VoteFormNode(template.Node):
    def __init__(self, obj, vote, next=None):
        self.obj = template.Variable(obj)
        self.vote = template.Variable(vote)
        self.next = next
        self.template = 'voting/form.html'

    def render(self, context):
        ctx = {
            'object': self.obj.resolve(context),
            'vote': self.vote.resolve(context)
        }
        if self.next:
            ctx.update({"next": self.next.resolve(context)})
        return template.loader.render_to_string(self.template, ctx,
            context_instance=context)
