from django.template.base import Node, Library, Variable
from django.template.base import TemplateSyntaxError
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from follow.models import Follow

register = Library()


@register.tag
def follow_form(parser, token):
    """
    Renders the following form. This can optionally take a success url.

    Usage ('next' is optional)::

        {% follow_form user object %}
        {% follow_form user object next %}

    """
    bits = token.split_contents()
    if len(bits) < 3:
        raise TemplateSyntaxError("'%s' takes at least two arguments"
                          " (user and object to follow)" % bits[0])
    elif len(bits) > 4:
        raise TemplateSyntaxError("'%s' takes at most three arguments." \
                                                                     % bits[0])
    user = bits[1]
    obj = bits[2]
    if len(bits) == 4:
        next = parser.compile_filter(bits[3])
    else:
        next = None
    return FollowFormNode(user, obj, next)


class FollowFormNode(Node):
    def __init__(self, user, obj, next=None):
        self.user = Variable(user)
        self.obj = Variable(obj)
        self.next = next
        self.template = "follow/form_new.html"

    def render(self, context):
        user = self.user.resolve(context)
        obj = self.obj.resolve(context)
        if Follow.objects.is_following(user, obj):
            btn_var = {"name": "unfollow", "value": _("Unfollow"),
                                            "class": "btn btn-primary"}
        else:
            btn_var = {"name": "follow", "value": _("Follow"),
                                            "class": "btn"}
        ctx = {"object": obj, "btn_var": btn_var}
        if self.next:
            ctx.update({"next": self.next.resolve(context)})
        return render_to_string(self.template, ctx, context_instance=context)
