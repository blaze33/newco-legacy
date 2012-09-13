from django.template.base import Node, Library, Variable
from django.template.base import TemplateSyntaxError
from django.template.loader import render_to_string

register = Library()


@register.tag
def vote_form(parser, token):
    """
    Renders the vote form.

    Usage ('next' is optional)::

        {% vote_form object vote %}
        {% vote_form object vote next %}

    """
    bits = token.split_contents()
    if len(bits) < 3:
        raise TemplateSyntaxError("'%s' takes at least two arguments"
                          " (object to vote on and current vote)" % bits[0])
    elif len(bits) > 4:
        raise TemplateSyntaxError("'%s' takes at most three arguments." \
                                                                     % bits[0])
    obj = bits[1]
    vote = bits[2]
    if len(bits) == 4:
        next = parser.compile_filter(bits[3])
    else:
        next = None
    return VoteFormNode(obj, vote, next)


class VoteFormNode(Node):
    def __init__(self, obj, vote, next=None):
        self.obj = Variable(obj)
        self.vote = Variable(vote)
        self.next = next
        self.template = 'voting/form.html'

    def render(self, context):
        ctx = {
            'object': self.obj.resolve(context),
            'vote': self.vote.resolve(context)
        }
        if self.next:
            ctx.update({"next": self.next.resolve(context)})
        return render_to_string(self.template, ctx, context_instance=context)
