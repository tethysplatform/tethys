from django import template
from django.template.defaultfilters import stringfilter
from django.conf import settings

import os

register = template.Library()


@register.filter
@stringfilter
def load_custom_css(var):
    if var.startswith('/'):
        var = var.lstrip('/')

    is_file = os.path.isfile(os.path.join(settings.STATIC_ROOT, var))

    if is_file:
        return '<link href="' + os.path.join('/static', var) + '" rel="stylesheet" />'

    else:
        for path in settings.STATICFILES_DIRS:
            is_file = os.path.isfile(os.path.join(path, var))
            if is_file:
                return '<link href="' + os.path.join('/static', var) + '" rel="stylesheet" />'

    return '<style>' + var + '</style>'
