import copy

from django.template.base import Library, Variable
from django.template.base import TemplateSyntaxError
from django.template.loader import render_to_string

from utils.follow import Follow
from utils.follow.constants import DEFAULT_CONF
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

        fields = ["next", "base_class", "success_class", "extra_class",
                  "tooltip_class", "quote_type"]
        for index, field in enumerate(fields):
            value = kwargs.get(field, None)
            value = args[index] if not value and len(args) > index else value
            setattr(self, field, value)

        is_following = Follow.objects.is_following(user, obj)
        buttons = copy.deepcopy(DEFAULT_CONF)
        for key in buttons.keys():
            if user == obj:
                buttons[key].update({"disabled": "disabled"})
            if self.base_class:
                buttons[key].update({"class": self.base_class})
            if self.extra_class:
                buttons[key].update({"extra_class": self.extra_class})
            tooltip_class = self.tooltip_class if self.tooltip_class else \
                buttons[key]["tooltip_class"]
            buttons[key].update({
                "class": buttons[key]["class"] + " " + tooltip_class})
            if key == "following" and self.success_class:
                buttons[key]["class"] += " " + self.success_class

        key = "follow" if is_following else "following"
        buttons[key]["class"] = buttons[key]["class"] + " hidden"

        ctx = {"object": obj, "buttons": buttons}
        if self.next:
            ctx.update({"next": self.next})

        html = render_to_string(self.template, ctx, context_instance=context)

        return self.render_output(context, html)


@register.tag
def follow_form(parser, token):
    """
    Renders the following form. This can optionally take a success url,
    an extra class for the follow button, and a tooltip class for tooltip
    position, or complety override the default btn + btn-primary behaviour

    Usage ('next' is optional)::

        {% follow_form user object %}
        {% follow_form user object next="" base_class="btn"
                success_class="btn-primary" tooltip_class="tooltip-top" %}

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
