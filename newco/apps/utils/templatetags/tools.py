import string

from django.template.base import Node, TemplateSyntaxError, kwarg_re
from django.template.loader import render_to_string
from django.utils.encoding import smart_str
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _, ungettext


class GenericNode(Node):

    quote_type = "double"

    def __init__(self, args, kwargs, asvar):
        self.args = args
        self.kwargs = kwargs
        self.asvar = asvar

    def resolve_template_args(self, context):
        args = [arg.resolve(context) for arg in self.args]
        kwargs = dict([(smart_str(k, 'ascii'), v.resolve(context))
                       for k, v in self.kwargs.items()])
        return [args, kwargs]

    def render_output(self, context, value):
        if self.quote_type == "single":
            value = value.replace("\"", "\'")
        if self.asvar:
            context[self.asvar] = mark_safe(value)
            return ""
        else:
            return mark_safe(value)


def get_node_extra_arguments(parser, bits, tag_name, max_args):
    args = []
    kwargs = {}
    asvar = None
    if len(bits) >= 2 and bits[-2] == 'as':
        asvar = bits[-1]
        bits = bits[:-2]

    if len(bits):
        if len(bits) <= max_args:
            for bit in bits:
                match = kwarg_re.match(bit)
                if not match:
                    err_msg = "Malformed arguments in '%s'" % tag_name
                    raise TemplateSyntaxError(err_msg)
                name, val = match.groups()
                if name:
                    kwargs[name] = parser.compile_filter(val)
                else:
                    args.append(parser.compile_filter(val))
        else:
            err_msg = "'%s' tag takes at most %d extra arguments." \
                % (tag_name, max_args)
            raise TemplateSyntaxError(err_msg)

    return [args, kwargs, asvar]


def generate_objs_sentence(obj_qs, obj_tpl, obj_tpl_name, max_nb=None, sep=" ",
                           obj_tpl_ctx={}, context=None):

    words = []
    for index, obj in enumerate(obj_qs):
        obj_tpl_ctx.update({obj_tpl_name: obj})
        words.append(render_to_string(obj_tpl, obj_tpl_ctx,
                     context_instance=context))

    sentence = ""
    if words:
        if sep == "text":
            if len(words) == 1:
                sentence = words[0]
            elif max_nb and len(words) > max_nb:
                sentence = ", ".join(words[:max_nb]) + "..."
            else:
                sentence = ", ".join(words[:-1]) + \
                    " " + _("and") + " " + words[-1]
        else:
            if max_nb:
                words = words[:max_nb]
            sentence = sep.join(words)
    return sentence


def get_content_source(content, display, color=None, context=None,
                       request=None, sep="text"):
    nb = [content.items.count(), content.tags.count()]
    prods_kwargs = {
        "obj_qs": content.items.all(), "obj_tpl_name": "object", "sep": sep,
        "obj_tpl": "items/_product_display.html", "context": context,
        "obj_tpl_ctx": {"display": display}
    }
    tags_kwargs = {
        "obj_qs": content.tags.all(), "obj_tpl_name": "tag",
        "obj_tpl": "tags/_tag_display.html", "sep": sep, "context": context,
        "obj_tpl_ctx": {"display": display}
    }

    if request:
        prods_kwargs.get("obj_tpl_ctx").update({"request": request})
        tags_kwargs.get("obj_tpl_ctx").update({"request": request})
    if color:
        prods_kwargs.get("obj_tpl_ctx").update({"color": color})

    words = []
    if sep == "text":
        if nb[0]:
            s = ungettext("about the product", "about the products", nb[0])\
                + " " + generate_objs_sentence(**prods_kwargs)
            words.append(s)
        if all(nb):
            words.append(" " + _("and") + " ")
        if nb[1]:
            s = ungettext("with the tag", "with the tags", nb[1])\
                + " " + generate_objs_sentence(**tags_kwargs)
            words.append(s)
    else:
        words.append(generate_objs_sentence(**prods_kwargs))
        if all(nb):
            words.append(sep)
        words.append(generate_objs_sentence(**tags_kwargs))

    return string.join(words, "")
