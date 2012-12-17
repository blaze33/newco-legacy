from django.utils.translation import ugettext_lazy as _

from model_utils import Choices

CURRENCIES = Choices(
    (0, "euro", _("Euro")),
    (1, "dollar", _("Dollar")),
    (2, "pound", _("Pound"))
)

AVAILABILITY_PATTERNS = {
    "exact": "{value} {unit}",
    "range": "{min_value}/{max_value} {unit}"
}

RE_AVAILABILITY_PATTERNS = {
    "exact": "(?P<value>\d+)\s(?P<unit>\w)",
    "range": "(?P<min_value>\d+)/(?P<max_value>\d+)\s(?P<unit>\w)"
}
