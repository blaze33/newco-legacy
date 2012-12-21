from django.template.base import Variable, Library, TemplateSyntaxError

from babel.numbers import format_currency

from affiliation import CURRENCIES
from utils.templatetags.tools import GenericNode, get_node_extra_arguments

register = Library()


class PriceNode(GenericNode):
    def __init__(self, value, *args, **kwargs):
        self.value = Variable(value)
        super(PriceNode, self).__init__(*args, **kwargs)

    def render(self, context):
        try:
            value = self.value.resolve(context)
            args, kwargs = self.resolve_template_args(context)
        except:
            return ""

        fields = ["currency", "language_code"]
        for index, field in enumerate(fields):
            val = kwargs.get(field, None)
            val = args[index] if not val and len(args) > index else val
            setattr(self, field, val)

        return self.render_output(
            context, format_price(value, self.currency, self.language_code))


@register.tag
def price(parser, token):
    """
    Return formatted currency value.

    This is a way to define links that aren't tied to a particular URL
    configuration::

        {% price value currency language_code %}

    The first argument is a decimal number.

    Other arguments are space-separated values. 'currency' is a
    affiliation.CURRENCIES choice associated with the price value.
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
    value = bits[1]
    bits = bits[2:]

    args, kwargs, asvar = get_node_extra_arguments(parser, bits, tag_name, 2)

    return PriceNode(value, args, kwargs, asvar)


def format_price(value, currency, language_code):
    price_kwargs = {}
    if currency == CURRENCIES.euro:
        price_kwargs.update({"currency": "EUR"})
    elif currency == CURRENCIES.dollar:
        price_kwargs.update({"currency": "USD"})
    elif currency == CURRENCIES.pound:
        price_kwargs.update({"currency": "GBP"})
    else:
        price_kwargs.update({"currency": "EUR"})

    if language_code == "fr":
        price_kwargs.update({"locale": "fr_FR"})
    elif language_code == "en":
        price_kwargs.update({"locale": "en_US"})
    else:
        price_kwargs.update({"locale": "fr_FR"})

    return format_currency(value, **price_kwargs)
