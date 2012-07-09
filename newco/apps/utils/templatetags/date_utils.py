from datetime import date, datetime

from django import template
from django.template import defaultfilters
from django.utils.translation import ungettext, ugettext as _
from django.utils.timezone import is_aware, utc

register = template.Library()


@register.filter
def datediff(value, arg=None):
    """
    For date values that are today, shows how many seconds, minutes or hours
    ago compared to current timestamp returns representing string.
    For yesterday or two days ago compared to present day returns representing
    string. Otherwise, returns a string formatted according to
    settings.DATE_FORMAT.
    """
    if not isinstance(value, date):  # datetime is a subclass of date
        return value

    now = datetime.now(utc if is_aware(value) else None)

    if value > now:
        return defaultfilters.date(value, arg)
    else:
        delta = now - value

    if delta.days > 2:
        return defaultfilters.date(value, arg)
    elif delta.days == 2:
        return _(u'2 days ago')
    elif delta.days == 1:
        return _(u'yesterday')
    else:
        if delta.seconds == 0:
            return _(u'now')
        elif delta.seconds < 60:
            return ungettext(
                u'a second ago', u'%(count)s seconds ago', delta.seconds
            ) % {'count': delta.seconds}
        elif delta.seconds // 60 < 60:
            count = delta.seconds // 60
            return ungettext(
                u'a minute ago', u'%(count)s minutes ago', count
            ) % {'count': count}
        else:
            count = delta.seconds // 60 // 60
            return ungettext(
                u'an hour ago', u'%(count)s hours ago', count
            ) % {'count': count}
