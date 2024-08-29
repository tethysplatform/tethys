from django import template
from django.template.defaultfilters import stringfilter
from django.conf import settings

import os

from ..static_finders import TethysStaticFinder

static_finder = TethysStaticFinder()

register = template.Library()


@register.filter
@stringfilter
def load_custom_css(var):
    if var.startswith(os.sep):
        var = var.lstrip(os.sep)

    is_file = os.path.isfile(
        os.path.join(settings.STATIC_ROOT, var)
    ) or static_finder.find(var)

    if is_file:
        return '<link href="' + os.path.join(os.sep, "static", var) + '" rel="stylesheet" />'

    else:
        for path in settings.STATICFILES_DIRS:
            is_file = os.path.isfile(os.path.join(path, var))
            if is_file:
                return (
                    '<link href="'
                    + os.path.join(os.sep, "static", var)
                    + '" rel="stylesheet" />'
                )

    return "<style>" + var + "</style>"
