# -*- coding: utf-8 -*-
from django.template import Library
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

from utils.hyphenate.tools import hyphenate

register = Library()


def softhyphen(value, language="en-us"):
    """
    Hyphenates html.
    """
    return mark_safe(hyphenate(value, language=language))
softhyphen.is_safe = True
softhyphen = stringfilter(softhyphen)
softhyphen = register.filter(softhyphen)
