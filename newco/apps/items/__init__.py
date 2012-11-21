from django.utils.translation import ugettext_lazy as _

from model_utils import Choices


STATUSES = Choices(
    (0, "draft", _("Draft")),
    # (1, "sandbox", _("Sandbox")),
    (2, "public", _("Public"))
)
