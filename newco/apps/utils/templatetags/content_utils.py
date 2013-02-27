import string

from django.core.urlresolvers import reverse
from django.template.base import Node, Library, Variable
from django.template.base import TemplateSyntaxError
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from django.contrib.auth.models import User

from account.utils import user_display
from gravatar.templatetags.gravatar import (gravatar_img_for_user,
                                            gravatar_profile_for_user)
from taggit.models import Tag

from items.models import Item, Content
from utils.hyphenate.tools import hyphenate
from utils.tools import get_class_name
from utils.templatetags.tools import (GenericNode, get_node_extra_arguments,
                                      generate_objs_sentence,
                                      get_content_source)

register = Library()


@register.filter
def to_class_name(value):
    return value._meta.module_name


@register.filter
def full_class_name(value):
    return get_class_name(value)


@register.filter
def verbose_name(value):
    return value._meta.verbose_name


@register.filter
def get_at_index(list, index):
    return list[index]


@register.filter
def getitem(item, string):
    return item.get(string, "")


@register.filter
def feed_template(value):
    return "items/feed_display/_%s.html" % value._meta.module_name


@register.assignment_tag
def get_content_url(content, display, item=None):
    if display == "detail":
        return content.get_absolute_url()
    elif display == "list" and item is not None:
        return content.get_product_related_url(item)
    return ""


class EditButtonsNode(GenericNode):

    template = "items/_edit_buttons.html"

    def __init__(self, user, obj, *args, **kwargs):
        self.user = Variable(user)
        self.obj = Variable(obj)
        super(EditButtonsNode, self).__init__(*args, **kwargs)

    def render(self, context):
        try:
            user = self.user.resolve(context)
            obj = self.obj.resolve(context)
            args, kwargs = self.resolve_template_args(context)
        except:
            return ""

        #TODO: More generically, implement a 'can_manage' permission
        if not (user.is_superuser or getattr(obj, "author", None) == user):
            return ""
        url_args = [obj._meta.module_name, obj.id]
        ctx = {"edit_url": reverse("item_edit", args=url_args),
               "delete_url": reverse("item_delete", args=url_args)}

        fields = ["edit_next", "delete_next"]
        for index, field in enumerate(fields):
            value = kwargs.get(field, None)
            value = args[index] if not value and len(args) > index else value
            if value:
                key = string.replace(field, "next", "url")
                ctx.update({key: "%s?next=%s" % (ctx.get(key), value)})

        html = render_to_string(self.template, ctx, context_instance=context)

        return self.render_output(context, html)


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
        {% edit_buttons user obj edit_next=var as html_var %}

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

        {% profile_pic <user> [size] [quote_type] %}

    Example::

        {% profile_pic request.user 48 %}
        {% profile_pic 'max' 48 'single' %}
    """
    img = gravatar_img_for_user(user, size, rating=None)
    if quote_type == "single":
        img = img.replace("\"", "\'")
    return mark_safe(img)


@register.simple_tag
def gravatar_profile_url(user):
    """
    Returns the user profile url at gravatar, or sign up url if not registered.

    Syntax::

        {% gravatar_profile_url <user> %}

    Example::

        {% gravatar_profile_url request.user %}
        {% gravatar_profile_url 'max' %}
    """
    data = gravatar_profile_for_user(user)
    if data == "User not found":
        url = u"https://fr.gravatar.com/site/signup"
    elif type(data) is dict:
        url = data["entry"][0]["profileUrl"]
    return url


@register.simple_tag
def favicon(url, size=16, quote_type="double"):
    """
    Returns the website's favicon of the given url.

    Syntax::

        {% favicon <url> [size] %}

    Example::

        {% favicon "http://www.google.fr" %}
        {% favicon myurl 62 %}
    """
    template = "favicon.html"
    icon_url = "https://getfavicon.appspot.com/%s" % url
    context = {"icon_url": icon_url, "size": size}
    favicon = render_to_string(template, context)
    if quote_type == "single":
        favicon = favicon.replace("\"", "\'")
    return mark_safe(favicon)


class URINode(GenericNode):
    def __init__(self, obj, request, *args, **kwargs):
        self.obj = Variable(obj)
        self.request = Variable(request)
        super(URINode, self).__init__(*args, **kwargs)

    def render(self, context):
        try:
            obj = self.obj.resolve(context)
            request = self.request.resolve(context)
        except:
            return ""
        if obj.__class__ is not Tag:
            url = obj.get_absolute_url()
        else:
            # Dirty. Check coop-tag
            url = reverse("tagged_items", args=[obj.slug])
        return self.render_output(context, request.build_absolute_uri(url))


@register.tag
def get_absolute_uri(parser, token):
    """
    Returns the full uri of an object. Value can be pasted in var.

    Syntax::

        {% get_absolute_uri object request %}

    Example::

        {% get_absolute_uri answer request as my_uri %}
    """
    bits = token.split_contents()
    if len(bits) != 3:
        raise TemplateSyntaxError("'%s' takes 2 arguments." % bits[0])
    tag_name = bits[0]
    obj = bits[1]
    request = bits[2]
    bits = bits[3:]

    args, kwargs, asvar = get_node_extra_arguments(parser, bits, tag_name, 0)

    return URINode(obj, request, args, kwargs, asvar)


class ObjectDisplayNode(GenericNode):
    def __init__(self, obj, display, *args, **kwargs):
        self.obj = Variable(obj)
        self.display = Variable(display)
        super(ObjectDisplayNode, self).__init__(*args, **kwargs)

    def render(self, context):
        try:
            obj = self.obj.resolve(context)
            display = self.display.resolve(context)
            args, kwargs = self.resolve_template_args(context)
        except:
            return ""

        ctx = {"object": obj, "display": display}

        color = kwargs.get("color", None)
        color = args[0] if not color and len(args) > 0 else color
        if color:
            ctx.update({"color": color})

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
        html = render_to_string(template, ctx, context_instance=context)

        return self.render_output(context, html)


@register.tag
def object_display(parser, token):
    """
    Renders the item link with or without its popover, depending on display.
    Can add a css defined color and paste html in a variable.

    Usage::

        {% object_display object display %}
        {% object_display object display color="blue" %}
        {% object_display object "list" "black" as user_popover %}

    """
    bits = token.split_contents()
    if len(bits) < 3:
        raise TemplateSyntaxError("'%s' takes at least 2 arguments." % bits[0])
    tag_name = bits[0]
    obj = bits[1]
    display = bits[2]
    bits = bits[3:]

    args, kwargs, asvar = get_node_extra_arguments(parser, bits, tag_name, 1)

    return ObjectDisplayNode(obj, display, args, kwargs, asvar)


class SourceDisplayNode(GenericNode):
    def __init__(self, obj, display, *args, **kwargs):
        self.obj = Variable(obj)
        self.display = Variable(display)
        super(SourceDisplayNode, self).__init__(*args, **kwargs)

    def render(self, context):
        try:
            obj = self.obj.resolve(context)
            display = self.display.resolve(context)
            args, kwargs = self.resolve_template_args(context)
        except:
            return ""

        sep = kwargs.get("sep", None)
        sep = args[1] if not sep and len(args) > 1 else sep

        kwargs = {}
        if sep:
            kwargs.update({"sep": sep})
        if not (obj.__class__ is Content or hasattr(obj, "content_ptr")):
            raise TemplateSyntaxError("'source_display' only renders "
                                      "Content instances")

        html = get_content_source(obj, display, context=context,
                                  **kwargs)

        return self.render_output(context, html)


@register.tag
def source_display(parser, token):
    """
    Renders the sources of a content object whether it be
    one or several products and/or one or several tags.
    Can add a separator (default is 'text') and paste html in a variable.

    Usage::

        {% source_display content display %}
        {% source_display content "list" as source %}
        {% source_display content "list" sep="," as source %}

    """
    bits = token.split_contents()
    if len(bits) < 3:
        raise TemplateSyntaxError("'%s' takes at least 2 arguments." % bits[0])
    tag_name = bits[0]
    obj = bits[1]
    display = bits[2]
    bits = bits[3:]

    args, kwargs, asvar = get_node_extra_arguments(parser, bits, tag_name, 1)

    return SourceDisplayNode(obj, display, args, kwargs, asvar)


class TagDisplayNode(GenericNode):
    def __init__(self, tag, *args, **kwargs):
        self.tag = Variable(tag)
        super(TagDisplayNode, self).__init__(*args, **kwargs)

    def render(self, context):
        try:
            tag = self.tag.resolve(context)
            args, kwargs = self.resolve_template_args(context)
        except:
            return ""

        template, ctx = ["tags/_tag_display.html", {"tag": tag}]
        fields = ["quote_type", "extra_class"]
        for index, field in enumerate(fields):
            value = kwargs.get(field, None)
            value = args[index] if not value and len(args) > index else value
            if not value:
                continue
            if field == "quote_type":
                setattr(self, field, value)
            elif field == "extra_class":
                ctx.update({field: value})

        html = render_to_string(template, ctx, context_instance=context)
        html = hyphenate(html)

        return self.render_output(context, html)


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


class TagsDisplayNode(GenericNode):
    def __init__(self, tags, *args, **kwargs):
        self.tags = Variable(tags)
        super(TagsDisplayNode, self).__init__(*args, **kwargs)

    def render(self, context):
        try:
            tags = self.tags.resolve(context)
            args, kwargs = self.resolve_template_args(context)
        except:
            return ""

        f_kwargs = {"queryset": tags.all(), "object_name": "tag",
                    "template": "tags/_tag_display.html", "context": context,
                    "container": "tags"}
        fields = ["max_nb", "quote_type", "sep", "extra_class"]
        for index, field in enumerate(fields):
            value = kwargs.get(field, None)
            value = args[index] if not value and len(args) > index else value
            if not value:
                continue
            if field == "extra_class":
                f_kwargs.update({"template_context": {field: value}})
            elif field == "quote_type":
                setattr(self, field, value)
            else:
                f_kwargs.update({field: value})

        html = generate_objs_sentence(**f_kwargs)
        # html = hyphenate(html)

        return self.render_output(context, html)


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


class ContentInfoNode(GenericNode):
    def __init__(self, content, display, *args, **kwargs):
        self.content = Variable(content)
        self.display = Variable(display)
        super(ContentInfoNode, self).__init__(*args, **kwargs)

    def render(self, context):
        try:
            content = self.content.resolve(context)
            display = self.display.resolve(context)
            args, kwargs = self.resolve_template_args(context)
        except:
            return ""

        pic_size = kwargs.get("pic_size", None)
        pic_size = args[0] if not pic_size and len(args) > 0 else pic_size

        template, author = ["content/info.html", content.author]
        ctx = {"pub_date": content.created}
        if "signature" in display or display == "detail":
            ctx.update({"case": "signature"})
            if display in ["signature", "detail"]:
                ctx.update({
                    "signature_author": True,
                    "signature_pic": True,
                    "author_name": user_display(author),
                    "reputation": author.reputation.reputation_incremented,
                    "author_url": author.get_absolute_url(),
                    "profile_pic": profile_pic(author, size=pic_size)
                })
            elif display == "signature-author":
                ctx.update({
                    "signature_author": True,
                    "author_name": user_display(author),
                    "reputation": author.reputation.reputation_incremented,
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
            ctx.update({
                "case": "header",
                # "author_name": user_display(author),
                # "author_url": author.get_absolute_url(),
                "author": author,
                "reputation": author.reputation.reputation_incremented,
                "about": author.get_profile().about
            })
        elif display in ["date", "list"]:
            ctx.update({"case": "date"})
        else:
            raise TemplateSyntaxError("'content_info': wrong display value.")
        return render_to_string(template, ctx, context_instance=context)


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
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least 2 arguments." % bits[0])
    tag_name = bits[0]
    content = bits[1]
    display = bits[2]
    bits = bits[3:]

    args, kwargs, asvar = get_node_extra_arguments(parser, bits, tag_name, 1)

    return ContentInfoNode(content, display, args, kwargs, asvar)


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
