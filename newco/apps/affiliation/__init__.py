from django.utils.translation import ugettext_lazy as _

from model_utils import Choices

CURRENCIES = Choices(
    (0, "euro", _("Euro")),
    (1, "dollar", _("Dollar")),
    (2, "pound", _("Pound"))
)
