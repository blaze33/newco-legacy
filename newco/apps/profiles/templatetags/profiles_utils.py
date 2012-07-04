from django import template

register = template.Library()



@register.tag
def profile_link(parser, token):
    """
    Renders the profile link with its popover.

    Usage::

        {% profile_link user xxx %}

    """
    bits = token.split_contents()
    return ProfileLinkNode(*bits[1:])


class ProfileLinkNode(template.Node):
    def __init__(self, usr):
        self.usr = template.Variable(usr)
        ##self.xxx = template.Variable(xxx)
        self.template = 'profiles/profile_link.html'

    def render(self, context):
        ctx = {
            'user': self.usr.resolve(context),
            ##'xxx': self.xxx.resolve(context)
        }
        return template.loader.render_to_string(self.template, ctx,
            context_instance=context)
