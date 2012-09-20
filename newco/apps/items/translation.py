from django.utils.translation import pgettext

ARTICLES = (
    pgettext("item", "the "),
    pgettext("question", "the "),
    pgettext("answer", "the "),
    pgettext("link", "the "),
    pgettext("feature", "the "),
)

DELETE = (
    pgettext("item", "The %(class)s <i>%(object)s</i> will be deleted:"),
    pgettext("question", "The %(class)s <i>%(object)s</i> will be deleted:"),
    pgettext("answer", "The %(class)s <i>%(object)s</i> will be deleted:"),
    pgettext("link", "The %(class)s <i>%(object)s</i> will be deleted:"),
    pgettext("feature", "The %(class)s <i>%(object)s</i> will be deleted:"),
)
