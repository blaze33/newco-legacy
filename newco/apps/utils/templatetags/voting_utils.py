from django.template.base import Library, Variable
from django.template.base import TemplateSyntaxError
from django.template.loader import render_to_string

from utils.templatetags.tools import GenericNode, get_node_extra_arguments

register = Library()


class VoteFormNode(GenericNode):

    template = "voting/form.html"

    def __init__(self, obj, vote, *args, **kwargs):
        self.obj = Variable(obj)
        self.vote = Variable(vote)
        super(VoteFormNode, self).__init__(*args, **kwargs)

    def render(self, context):
        try:
            ctx = {"object": self.obj.resolve(context),
                   "vote": self.vote.resolve(context)}
            args, kwargs = self.resolve_template_args(context)
        except:
            return ""

        next = kwargs.get("next", None)
        next = args[0] if not next and len(args) > 0 else next

        if next:
            ctx.update({"next": next})

        html = render_to_string(self.template, ctx, context_instance=context)

        return self.render_output(context, html)


@register.tag
def vote_form(parser, token):
    """
    Renders the vote form.
    Can add redirection paths after success. Can store the html in a variable.

    Usage::

        {% vote_form object vote %}
        {% vote_form object vote next %}
        {% vote_form object vote "/" as form %}

    """
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least 2 arguments." % bits[0])
    tag_name = bits[0]
    obj = bits[1]
    vote = bits[2]
    bits = bits[3:]

    args, kwargs, asvar = get_node_extra_arguments(parser, bits, tag_name, 1)

    return VoteFormNode(obj, vote, args, kwargs, asvar)
