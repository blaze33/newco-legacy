from django.template.base import Node, Library, TemplateSyntaxError
from django.utils.encoding import smart_str

from babel.numbers import format_currency

from affiliation.models import AffiliationItemBase
from utils.tools import get_node_extra_arguments

register = Library()


class PriceNode(Node):
    def __init__(self, value, args, kwargs, asvar):
        self.value = value
        self.args = args
        self.kwargs = kwargs
        self.asvar = asvar

    def render(self, context):
        value = self.value.resolve(context)
        args = [arg.resolve(context) for arg in self.args]
        kwargs = dict([(smart_str(k, 'ascii'), v.resolve(context))
                       for k, v in self.kwargs.items()])

        currency = kwargs.get("currency", "")
        language_code = kwargs.get("language_code", "")
        if not currency and len(args) >= 1:
            currency = args[0]
        if not language_code and len(args) == 2:
            language_code = args[1]

        kwargs = dict()

        currencies = AffiliationItemBase.CURRENCIES
        if currency == currencies.euro:
            kwargs.update({"currency": "EUR"})
        elif currency == currencies.dollar:
            kwargs.update({"currency": "USD"})
        elif currency == currencies.pound:
            kwargs.update({"currency": "GBP"})
        else:
            kwargs.update({"currency": "EUR"})

        if language_code == "fr":
            kwargs.update({"locale": "fr_FR"})
        elif language_code == "en":
            kwargs.update({"locale": "en_US"})

        formatted_price = format_currency(value, **kwargs)

        if self.asvar:
            context[self.asvar] = formatted_price
            return ""
        else:
            return formatted_price


@register.tag
def price(parser, token):
    """
    Return formatted currency value.

    This is a way to define links that aren't tied to a particular URL
    configuration::

        {% price value currency language_code %}

    The first argument is a decimal number.

    Other arguments are space-separated values. 'currency' is a
    AffiliationItemBase.CURRENCIES choice associated with the price value.
    'language_code' is the language convention used for the display.
    Don't mix positional and keyword arguments.

    'currency' and 'language_code' are not mandatory. 'currency' defaults to
    euro while 'language_code' defaults to environment variable 'LC_NUMERIC'.

    For example::

        {% price value currency language_code %}
                with value = Decimal("101.34")
                     currency = AffiliationItemBase.dollar
                     language_code = 'fr'

        will give u'101,34\xa0$US'

    """
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument"
                                  " (price to display)" % bits[0])
    tag_name = bits[0]
    value = parser.compile_filter(bits[1])
    bits = bits[2:]

    args, kwargs, asvar = get_node_extra_arguments(parser, bits, tag_name, 2)

    return PriceNode(value, args, kwargs, asvar)
