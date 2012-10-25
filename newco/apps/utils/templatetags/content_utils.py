import string

from django.template.base import Node, Library, Variable
from django.template.base import TemplateSyntaxError, VariableDoesNotExist
from django.template.loader import render_to_string
from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _, ungettext

from django.contrib.auth.models import User

from account.utils import user_display
from gravatar.templatetags.gravatar import gravatar_img_for_user

from items.models import Item, Content
from utils.tools import get_node_extra_arguments

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
def edit(item_name, item_id, edit_next=None):
    return {
        'item_name': item_name,
        'item_id': item_id,
        'edit_next': edit_next,
    }


@register.simple_tag
def profile_pic(user, size=None, quote_type="double"):
    """
    Returns the user profile picture. Only supports gravatar for now.

    Syntax::

        {% profile_pic_for_user <user> [size] %}

    Example::

        {% profile_pic_for_user request.user 48 %}
        {% profile_pic_for_user 'max' 48 %}
    """
    img = gravatar_img_for_user(user, size, rating=None)
    if quote_type == "single":
        img = img.replace("\"", "\'")
    return img


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

        nb = [obj.items.count(), obj.tags.count()]
        prods_kwargs = {
            "obj_qs": obj.items.all(), "obj_tpl_name": "object", "sep": "text",
            "obj_tpl": "items/_product_display.html",
            "obj_tpl_ctx": {"display": display, "color": color},
        }
        tags_kwargs = {
            "obj_qs": obj.tags.all(), "obj_tpl_name": "tag",
            "obj_tpl": "tags/_tag_display.html", "sep": "text"
        }

        words = list()
        if nb[0]:
            s = ungettext("about the product", "about the products", nb[0])\
                + " " + generate_objs_sentence(context, **prods_kwargs)
            words.append(s)
        if all(n for n in nb):
            words.append(" " + _("and") + " ")
        if nb[1]:
            s = ungettext("with the tag", "with the tags", nb[1])\
                + " " + generate_objs_sentence(context, **tags_kwargs)
            words.append(s)

        return string.join(words, "")


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

        args = [arg.resolve(context) for arg in self.args]
        kwargs = dict([(smart_str(k, 'ascii'), v.resolve(context))
                       for k, v in self.kwargs.items()])

        f_kwargs = {"obj_qs": tags.all(), "obj_tpl": "tags/_tag_display.html",
                    "obj_tpl_name": "tag"}
        fields = ["max_nb", "quote_type", "sep", "extra_class"]
        for index, field in enumerate(fields):
            value = kwargs.get(field, None)
            if not value and len(args) > index:
                value = args[index]
            if value:
                if field != "extra_class":
                    f_kwargs.update({field: value})
                else:
                    f_kwargs.update({"obj_tpl_ctx": {field: value}})

        return generate_objs_sentence(context, **f_kwargs)


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

    """
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least 1 arguments." % bits[0])
    elif len(bits) > 6:
        raise TemplateSyntaxError("'%s' takes at most 5 arguments." % bits[0])
    tag_name = bits[0]
    tags = bits[1]
    bits = bits[2:]

    args, kwargs, asvar = get_node_extra_arguments(parser, bits, tag_name, 4)

    return TagsDisplayNode(tags, args, kwargs, asvar)


def generate_objs_sentence(context, obj_qs, obj_tpl, obj_tpl_name, max_nb=None,
                           quote_type="double", sep=" ", obj_tpl_ctx={}):

    qs_length = obj_qs.count()
    if not qs_length:
        return ""
    max_nb = qs_length if not max_nb else max_nb

    if sep == "text":
        sep_list = [", "] * qs_length
        sep_list[-1] = " " + _("and") + " "
    else:
        sep_list = [sep] * qs_length

    sentence = ""
    for index, obj in enumerate(obj_qs):
        obj_tpl_ctx.update({obj_tpl_name: obj})
        s = render_to_string(obj_tpl, obj_tpl_ctx, context_instance=context)
        sentence = sentence + sep_list[index] + s if index else s
        if index + 1 == max_nb:
            break

    if quote_type == "single":
        sentence = sentence.replace("\"", "\'")
    return sentence


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
