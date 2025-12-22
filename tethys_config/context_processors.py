"""
********************************************************************************
* Name: context_processors.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""

import datetime as dt
import re
from django.conf import settings
from tethys_portal.optional_dependencies import optional_import, has_module
from tethys_apps.utilities import get_configured_standalone_app


def tethys_global_settings_context(request):
    """
    Add the current Tethys app metadata to the template context.
    """
    from .models import Setting

    # optional imports
    TermsAndConditions = optional_import(
        "TermsAndConditions", from_module="termsandconditions.models"
    )

    # Get settings
    site_globals = Setting.as_dict()

    # Set default settings
    if not site_globals.get("primary_color"):
        site_globals["primary_color"] = "#0a62a9"

    if not site_globals.get("secondary_color"):
        site_globals["secondary_color"] = "#a2d6f9"

    if not site_globals.get("background_color"):
        site_globals["background_color"] = "#fefefe"

    if not site_globals.get("primary_text_color"):
        site_globals["primary_text_color"] = "#ffffff"

    if not site_globals.get("primary_text_hover_color"):
        site_globals["primary_text_hover_color"] = "#eeeeee"

    if not site_globals.get("secondary_text_color"):
        site_globals["secondary_text_color"] = "#212529"

    if not site_globals.get("secondary_text_hover_color"):
        site_globals["secondary_text_hover_color"] = "#aaaaaa"

    # Get terms and conditions
    if has_module(TermsAndConditions):
        site_globals.update({"documents": TermsAndConditions.get_active_terms_list()})

    # Override settings for single app mode
    if not settings.MULTIPLE_APP_MODE:
        configured_single_app = get_configured_standalone_app()
        brand_image = site_globals.get("brand_image", "")
        brand_text = site_globals.get("brand_text")
        site_title = site_globals.get("site_title")
        if configured_single_app and (
            not brand_image
            or re.match(r"/tethys_portal/images/tethys-logo-\d{2}.png", brand_image)
        ):
            site_globals["brand_image"] = configured_single_app.icon
        if configured_single_app and (not brand_text or brand_text == "Tethys Portal"):
            site_globals["brand_text"] = configured_single_app.name
        if configured_single_app and (not site_title or site_title == "Tethys Portal"):
            site_globals["site_title"] = configured_single_app.name

    context = {
        "site_globals": site_globals,
        "site_defaults": {
            "copyright": f"Copyright © {dt.datetime.now(dt.timezone.utc):%Y} Your Organization",
        },
    }

    return context
