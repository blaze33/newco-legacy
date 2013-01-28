from django.utils.translation import ugettext_lazy as _, pgettext

DEFAULT_CONF = {
    "follow": {
        "class": "btn",
        "value": pgettext("Follow button", "Follow"),
        "title": _("Click to follow"),
        "tooltip_class": "tooltip-top",
    },
    "following": {
        "class": "btn btn-primary",
        "value": pgettext("Follow button", "Following"),
        "title": _("Click to unfollow"),
        "tooltip_class": "tooltip-top",
    }
}
