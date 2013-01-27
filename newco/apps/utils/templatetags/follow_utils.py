from django.template.base import Library, Variable
from django.template.base import TemplateSyntaxError
from django.template.loader import render_to_string
from django.utils.translation import pgettext
from django.utils.translation import ugettext_lazy as _

from follow.models import Follow
from utils.templatetags.tools import GenericNode, get_node_extra_arguments

register = Library()


class FollowFormNode(GenericNode):

    template = "follow/form.html"

    def __init__(self, user, obj, *args, **kwargs):
        self.user = Variable(user)
        self.obj = Variable(obj)
        super(FollowFormNode, self).__init__(*args, **kwargs)

    def render(self, context):
        try:
            user = self.user.resolve(context)
            obj = self.obj.resolve(context)
            args, kwargs = self.resolve_template_args(context)
        except:
            return ""

        fields = ["next", "extra_class", "tooltip_class", "quote_type"]
        for index, field in enumerate(fields):
            value = kwargs.get(field, None)
            value = args[index] if not value and len(args) > index else value
            setattr(self, field, value)

        ctx, btn = [{}, {"class": "btn"}]
        if user == obj:
            btn.update({"disabled": "disabled"})
        if self.extra_class:
            btn.update({"extra_class": self.extra_class})
        if Follow.objects.is_following(user, obj):
            btn.update({"name": "unfollow",
                        "value": pgettext("Follow button", "Following"),
                        "class": btn.get("class") + " btn-primary"})
            tooltip = {"title": _("Click to unfollow")}
            tooltip_class = self.tooltip_class if self.tooltip_class \
                else "tooltip-top"
            tooltip.update({"class": tooltip_class})
            ctx.update({"tooltip": tooltip})
        else:
            btn.update({"name": "follow",
                        "value": pgettext("Follow button", "Follow")})

        ctx.update({"object": obj, "btn": btn})
        if self.next:
            ctx.update({"next": self.next})

        html = render_to_string(self.template, ctx, context_instance=context)

        return self.render_output(context, html)


@register.tag
def follow_form(parser, token):
    """
    Renders the following form. This can optionally take a success url,
    an extra class for the follow button, and a tooltip class for tooltip
    position

    Usage ('next' is optional)::

        {% follow_form user object %}
        {% follow_form user object next="" extra_class=""
                tooltip_class="tooltip-top" %}

    """
    bits = token.split_contents()
    if len(bits) < 3:
        raise TemplateSyntaxError("'%s' takes at least two arguments"
                                  " (user and object to follow)" % bits[0])
    tag_name = bits[0]
    user = bits[1]
    obj = bits[2]
    bits = bits[3:]

    args, kwargs, asvar = get_node_extra_arguments(parser, bits, tag_name, 2)

    return FollowFormNode(user, obj, args, kwargs, asvar)
