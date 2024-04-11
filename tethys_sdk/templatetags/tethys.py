"""
********************************************************************************
* Name: tethys.py
* Author: Scott Christensen
* Created On: April 2024
* Copyright:
* License: BSD 2-Clause
********************************************************************************
"""

from tethys_apps.templatetags.app_theme import register as app_theme_library
from tethys_apps.templatetags.humanize import register as humanize_library
from tethys_apps.templatetags.site_settings import register as site_settings_library
from tethys_apps.templatetags.tags import register as tags_library
from tethys_gizmos.templatetags.tethys_gizmos import register as gizmos_library

from django import template

libraries = (
    app_theme_library,
    humanize_library,
    site_settings_library,
    tags_library,
    gizmos_library,
)

register = template.Library()
register.tags = {k: v for lib in libraries for k, v in lib.tags.items()}
register.filters = {k: v for lib in libraries for k, v in lib.filters.items()}
