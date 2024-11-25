from django import template
from django.template.defaultfilters import stringfilter
from django.conf import settings

from pathlib import Path

from ..static_finders import TethysStaticFinder

static_finder = TethysStaticFinder()

register = template.Library()


@register.filter
@stringfilter
def load_custom_css(var):
    if var.startswith("/"):
        var = var.lstrip("/")

    if (Path(settings.STATIC_ROOT) / var).is_file() or static_finder.find(var):
        return f'<link href="/static/{var}" rel="stylesheet" />'

    else:
        for path in settings.STATICFILES_DIRS:
            if (Path(path) / var).is_file():
                return f'<link href="/static/{var}" rel="stylesheet" />'

    return "<style>" + var + "</style>"
