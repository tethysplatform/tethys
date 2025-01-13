import logging
from pathlib import Path

from django import template
from django.template.defaultfilters import stringfilter
from django.conf import settings

from ..static_finders import TethysStaticFinder

static_finder = TethysStaticFinder()

register = template.Library()

log = logging.getLogger(f"tethys.{__name__}")


@register.filter
@stringfilter
def load_custom_css(var):
    """Load Custom Styles defined in Tethys Portal -> Site Settings

    Args:
        var: a filename of CSS to load or CSS text to embed into the page

    Returns:
        a string of HTML that either embeds CSS text or points to a file

    """
    if not var.strip():
        return ""
    if var.startswith("/"):
        var = var.lstrip("/")

    try:
        # Check if var is a path to a file, if so return a link tag to the file
        if (Path(settings.STATIC_ROOT) / var).is_file() or static_finder.find(var):
            return f'<link href="/static/{var}" rel="stylesheet" />'

        for path in settings.STATICFILES_DIRS:
            if (Path(path) / var).is_file():
                return f'<link href="/static/{var}" rel="stylesheet" />'
    # If the string is too long for a file path, which could happen if it is CSS,
    # an OSError will be raised during the file path checks. This could also happen
    # if a lengthy file path is given or is otherwise invalid.
    except OSError as e:
        oserror_exception = str(e)
    else:
        oserror_exception = ""

    # Verify the string is CSS and log warning if it is not
    common_css_chars = "{};,"
    if not any(c in var for c in common_css_chars):
        # This appears to be a filename and not a CSS string
        log.warning(
            f"Could not load file '{var}' for custom styles: {oserror_exception}"
        )
        return ""

    return "<style>" + var + "</style>"
