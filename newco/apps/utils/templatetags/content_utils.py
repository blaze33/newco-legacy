import string

from django.core.urlresolvers import reverse
from django.template.base import Node, Library, Variable
from django.template.base import TemplateSyntaxError, VariableDoesNotExist
from django.template.loader import render_to_string
from django.utils.encoding import smart_str

from django.contrib.auth.models import User

from account.utils import user_display
from gravatar.templatetags.gravatar import gravatar_img_for_user

from items.models import Item, Content
from utils.tools import (get_node_extra_arguments, resolve_template_args,
                         generate_objs_sentence, get_content_source)

register = Library()


@register.filter
def to_app_label(value):
    return value._meta.app_label


@register.filter
def to_class_name(value):
    return value._meta.module_name


@register.filter
def verbose_name(value):
    return value._meta.verbose_name


@register.filter
def get_at_index(list, index):
    return list[index]


@register.filter
def getitem(item, string):
    return item.get(string, "")


@register.inclusion_tag('items/_tag_edit.html')
def edit(item_name, item_id, edit_next=None, delete_next=None):
    return {
        'item_name': item_name,
        'item_id': item_id,
        'edit_next': edit_next,
    }


class EditButtonsNode(Node):
    def __init__(self, user, obj, args, kwargs, asvar):
        self.user = Variable(user)
        self.obj = Variable(obj)
        self.args = args
        self.kwargs = kwargs
        self.asvar = asvar

    def render(self, context):
        try:
            user = self.user.resolve(context)
            obj = self.obj.resolve(context)
        except:
            return ""

        #TODO: More generically, implement a 'can_manage' permission
        if not (user.is_superuser or getattr(obj, "author", None) == user):
            return ""

        args, kwargs = resolve_template_args(context, self.args, self.kwargs)

        url_args = [obj._meta.module_name, obj.id]
        ctx = {"edit_url": reverse("item_edit", args=url_args),
               "delete_url": reverse("item_delete", args=url_args)}

        template = "items/_edit_buttons.html"

        fields = ["edit_next", "delete_next"]
        for index, field in enumerate(fields):
            value = kwargs.get(field, None)
            value = args[index] if not value and len(args) > index else value
            if value:
                key = string.replace(field, "next", "url")
                ctx.update({key: "%s?next=%s" % (ctx.get(key), value)})

        html = render_to_string(template, ctx, context_instance=context)

        if self.asvar:
            context[self.asvar] = html
            return ""
        else:
            return html


@register.tag
def edit_buttons(parser, token):
    """
    Renders two buttons (edit and delete), using _edit_buttons template,
    given a user (client side) and an editable object.
    Can add redirection paths after success. Can store the html in a variable.

    Usage::

        {% edit_buttons user obj %}
        {% edit_buttons user obj edit_next="" delete_next="" %}
        {% edit_buttons user obj "/content" delete_next="/" %}
        {% edit_buttons user obj edit_next={{ var1 }} as var2 %}

    """
    bits = token.split_contents()
    if len(bits) < 3:
        raise TemplateSyntaxError("'%s' takes at least 2 arguments." % bits[0])
    tag_name = bits[0]
    user = bits[1]
    obj = bits[2]
    bits = bits[3:]

    args, kwargs, asvar = get_node_extra_arguments(parser, bits, tag_name, 2)

    return EditButtonsNode(user, obj, args, kwargs, asvar)


@register.simple_tag
def profile_pic(user, size=None, quote_type="double"):
    """
    Returns the user profile picture. Only supports gravatar for now.

    Syntax::

        {% profile_pic <user> [size] %}

    Example::

        {% profile_pic request.user 48 %}
        {% profile_pic 'max' 48 %}
    """
    img = gravatar_img_for_user(user, size, rating=None)
    if quote_type == "single":
        img = img.replace("\"", "\'")
    return img


class URINode(Node):
    def __init__(self, obj, request):
        self.obj = Variable(obj)
        self.request = Variable(request)

    def render(self, context):
        try:
            obj = self.obj.resolve(context)
            request = self.request.resolve(context)
        except:
            return ""
        return request.build_absolute_uri(obj.get_absolute_url())


@register.tag
def get_absolute_uri(parser, token):
    """
    Returns the full uri of an object.

    Syntax::

        {% get_absolute_uri object request %}

    Example::

        {% get_absolute_uri answer request %}
    """
    bits = token.split_contents()
    if len(bits) != 3:
        raise TemplateSyntaxError("'%s' takes 2 arguments." % bits[0])
    obj = bits[1]
    request = bits[2]
    return URINode(obj, request)


class ObjectDisplayNode(Node):
    def __init__(self, obj, display, color=None):
        self.obj = Variable(obj)
        self.display = Variable(display)
        self.color = Variable(color) if color else None

    def render(self, context):
        try:
            obj = self.obj.resolve(context)
        except VariableDoesNotExist:
            return ""
        else:
            if not obj:
                return ""
            display = self.display.resolve(context)
            color = self.color.resolve(context) if self.color else None
            ctx = {"object": obj, "display": display, "color": color}
            if obj.__class__ is Item:
                template = "items/_product_display.html"
            elif obj.__class__ is User:
                template = "profiles/_profile_display.html"
                skills = obj.get_profile().skills
                ctx.update({"username": user_display(obj)})
                if skills.count():
                    ctx.update({"skills": skills})
            else:
                raise TemplateSyntaxError("'object_display' only renders Item "
                                          "and User instances")
            return render_to_string(template, ctx, context_instance=context)


@register.tag
def object_display(parser, token):
    """
    Renders the item link with or without its popover, depending on display.
    Can add a css defined color

    Usage::

        {% object_display object display %}
        {% object_display object display color %}

    """
    bits = token.split_contents()
    if len(bits) < 3:
        raise TemplateSyntaxError("'%s' takes at least 2 arguments." % bits[0])
    elif len(bits) > 4:
        raise TemplateSyntaxError("'%s' takes at most 3 arguments." % bits[0])
    obj = bits[1]
    display = bits[2]
    link_color = bits[3] if len(bits) == 4 else None
    return ObjectDisplayNode(obj, display, link_color)


class SourceDisplayNode(Node):
    def __init__(self, obj, display, color=None):
        self.obj = Variable(obj)
        self.display = Variable(display)
        self.color = Variable(color) if color else None

    def render(self, context):
        try:
            obj = self.obj.resolve(context)
            if not obj:
                return ""
        except VariableDoesNotExist:
            return ""

        display = self.display.resolve(context)
        color = self.color.resolve(context) if self.color else None
        if not (obj.__class__ is Content or hasattr(obj, "content_ptr")):
            raise TemplateSyntaxError("'source_display' only renders "
                                      "Content instances")

        return get_content_source(obj, display, color=color, context=context)


@register.tag
def source_display(parser, token):
    """
    Renders the sources of a content object whether it be
    one or several products and/or one or several tags.
    Can add a css defined color

    Usage::

        {% source_display content display %}
        {% source_display content display color %}

    """
    bits = token.split_contents()
    if len(bits) < 3:
        raise TemplateSyntaxError("'%s' takes at least 2 arguments." % bits[0])
    elif len(bits) > 4:
        raise TemplateSyntaxError("'%s' takes at most 3 arguments." % bits[0])
    obj = bits[1]
    display = bits[2]
    link_color = bits[3] if len(bits) == 4 else None
    return SourceDisplayNode(obj, display, link_color)


class TagDisplayNode(Node):
    def __init__(self, tags, args, kwargs, asvar):
        self.tag = Variable(tags)
        self.args = args
        self.kwargs = kwargs
        self.asvar = asvar

    def render(self, context):
        try:
            tag = self.tag.resolve(context)
            if not tag:
                return ""
        except VariableDoesNotExist:
            return ""

        args, kwargs = resolve_template_args(context, self.args, self.kwargs)

        template = "tags/_tag_display.html"
        ctx = {"tag": tag}
        fields = ["quote_type", "extra_class"]
        for index, field in enumerate(fields):
            value = kwargs.get(field, None)
            value = args[index] if not value and len(args) > index else value
            if value and field == "extra_class":
                ctx.update({field: value})
            elif field == "quote_type":
                quote_type = value if value else "double"

        html = render_to_string(template, ctx, context_instance=context)

        if quote_type == "single":
            html = html.replace("\"", "\'")

        if self.asvar:
            context[self.asvar] = html
            return ""
        else:
            return html


@register.tag
def tag_display(parser, token):
    """
    Renders a tag using tag_display template.
    Can add a quote type (single or double), and an extra class parameter
    for the tag template. Can store the html in a variable.

    Usage::

        {% tag_display tag %}
        {% tag_display tag quote_type="double" extra_class="" %}
        {% tag_display tag "simple" extra_class="" as tag_html %}

    """
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least 1 arguments." % bits[0])
    tag_name = bits[0]
    tag = bits[1]
    bits = bits[2:]

    args, kwargs, asvar = get_node_extra_arguments(parser, bits, tag_name, 2)

    return TagDisplayNode(tag, args, kwargs, asvar)


class TagsDisplayNode(Node):
    def __init__(self, tags, args, kwargs, asvar):
        self.tags = Variable(tags)
        self.args = args
        self.kwargs = kwargs
        self.asvar = asvar

    def render(self, context):
        try:
            tags = self.tags.resolve(context)
            if not tags:
                return ""
        except VariableDoesNotExist:
            return ""

        args, kwargs = resolve_template_args(context, self.args, self.kwargs)

        f_kwargs = {"obj_qs": tags.all(), "obj_tpl": "tags/_tag_display.html",
                    "obj_tpl_name": "tag", "context": context}
        fields = ["max_nb", "quote_type", "sep", "extra_class"]
        for index, field in enumerate(fields):
            value = kwargs.get(field, None)
            value = args[index] if not value and len(args) > index else value
            if field != "extra_class" and value:
                f_kwargs.update({field: value})
            elif value:
                f_kwargs.update({"obj_tpl_ctx": {field: value}})

        sentence = generate_objs_sentence(**f_kwargs)

        if self.asvar:
            context[self.asvar] = sentence
            return ""
        else:
            return sentence


@register.tag
def tags_display(parser, token):
    """
    Renders the tags contained in a TaggableManager using tag_display template.
    Can add a max number of tags displayed condition, a quote type (single or
    double), an extra class parameter for the tag template, a separator
    displayed between tags

    Usage::

        {% tags_display tags %}
        {% tags_display tags max_nb=None quote_type="double" sep=" "
            extra_class="" %}
        {% tags_display tags 4 sep=" " as tags_html %}

    """
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least 1 arguments." % bits[0])
    tag_name = bits[0]
    tags = bits[1]
    bits = bits[2:]

    args, kwargs, asvar = get_node_extra_arguments(parser, bits, tag_name, 4)

    return TagsDisplayNode(tags, args, kwargs, asvar)


class ContentInfoNode(Node):
    def __init__(self, content, display, pic_size=None):
        self.content = Variable(content)
        self.display = display
        self.pic_size = pic_size
        self.template = "content/info.html"

    def render(self, context):
        content = self.content.resolve(context)
        display = smart_str(self.display.resolve(context), 'ascii')
        if self.pic_size:
            pic_size = self.pic_size.resolve(context)
        else:
            pic_size = None
        author = content.author
        if "signature" in display:
            ctx = {"pub_date": content.pub_date, "signature": True}
            if display == "signature":
                ctx.update({
                    "signature_author": True,
                    "signature_pic": True,
                    "author_name": user_display(author),
                    "author_url": author.get_absolute_url(),
                    "profile_pic": profile_pic(author, size=pic_size)
                })
            elif display == "signature-author":
                ctx.update({
                    "signature_author": True,
                    "author_name": user_display(author),
                    "author_url": author.get_absolute_url()
                })
            elif display == "signature-pic":
                ctx.update({
                    "signature_pic": True,
                    "profile_pic": profile_pic(author, size=pic_size)
                })
            else:
                raise TemplateSyntaxError("'content_info': wrong display.")
        elif display == "header":
            ctx = {
                "header": True,
                "author_name": user_display(author),
                "author_url": author.get_absolute_url(),
                "about": author.get_profile().about
            }
        else:
            raise TemplateSyntaxError("'content_info': wrong display value.")
        return render_to_string(self.template, ctx, context_instance=context)


@register.tag
def content_info(parser, token):
    """
    Displays content creation related info: author, creation date...

    Usage ('pic_size' is optional)::

        {% content_info content display %}
        {% content_info content display pic_size %}

        where display can be: "signature", "signature-author", "signature-pic"
        "header"

    """
    bits = token.split_contents()
    if len(bits) < 3:
        raise TemplateSyntaxError("'%s' takes at least 2 arguments." % bits[0])
    elif len(bits) > 4:
        raise TemplateSyntaxError("'%s' takes at most 3 arguments." % bits[0])
    content = bits[1]
    display = parser.compile_filter(bits[2])
    if len(bits) == 4:
        pic_size = parser.compile_filter(bits[3])
    else:
        pic_size = None
    return ContentInfoNode(content, display, pic_size)


class RangeNode(Node):
    def __init__(self, num, context_name):
        self.num, self.context_name = num, context_name

    def render(self, context):
        context[self.context_name] = range(int(self.num))
        return ""


@register.tag
def num_range(parser, token):
    """
    Takes a number and iterates and returns a range (list) that can be
    iterated through in templates

    Syntax:
    {% num_range 5 as some_range %}

    {% for i in some_range %}
      {{ i }}: Something I want to repeat\n
    {% endfor %}

    Produces:
    0: Something I want to repeat
    1: Something I want to repeat
    2: Something I want to repeat
    3: Something I want to repeat
    4: Something I want to repeat
    """
    try:
        fnctn, num, trash, context_name = token.split_contents()
    except ValueError:
        raise TemplateSyntaxError("%s takes the syntax %s number_to_iterate\
            as context_variable" % (fnctn, fnctn))
    if not trash == 'as':
        raise TemplateSyntaxError("%s takes the syntax %s number_to_iterate\
            as context_variable" % (fnctn, fnctn))
    return RangeNode(num, context_name)
