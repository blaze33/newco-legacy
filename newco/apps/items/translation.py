from django.utils.translation import pgettext

ARTICLES = (
    pgettext("item", "the "),
    pgettext("question", "the "),
    pgettext("answer", "the "),
)

CREATED = (
    pgettext("item", "created"),
    pgettext("question", "created"),
    pgettext("answer", "created"),
)

UPDATED = (
    pgettext("item", "updated"),
    pgettext("question", "updated"),
    pgettext("answer", "updated"),
)

DELETE = (
    pgettext("item", "The %(class)s <i>%(object)s</i> will be deleted:"),
    pgettext("question", "The %(class)s <i>%(object)s</i> will be deleted:"),
    pgettext("answer", "The %(class)s <i>%(object)s</i> will be deleted:"),
)
