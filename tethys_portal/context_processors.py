"""
********************************************************************************
* Name: context_processors.py
* Author: Scott Christensen
* Created On: 2023
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""

from .optional_dependencies import has_module
from django.conf import settings
from django.contrib import messages
from tethys_apps.utilities import get_configured_standalone_app


def tethys_portal_context(request):
    idps = (
        settings.SOCIAL_AUTH_SAML_ENABLED_IDPS
        if hasattr(settings, "SOCIAL_AUTH_SAML_ENABLED_IDPS")
        else {}
    )

    configured_single_app = None
    if not settings.MULTIPLE_APP_MODE:
        configured_single_app = get_configured_standalone_app()
        if not configured_single_app:
            messages.warning(
                request,
                "MULTIPLE_APP_MODE is disabled but there is no Tethys application installed.",
            )

    show_app_library_button = (
        True
        if settings.MULTIPLE_APP_MODE
        and (
            settings.ENABLE_OPEN_PORTAL
            or (
                getattr(request, "user", None)
                and request.user.is_authenticated
                and request.user.is_active
            )
        )
        else False
    )

    context = {
        "has_analytical": has_module("analytical"),
        "has_terms": has_module("termsandconditions")
        and getattr(request, "user", None) is not None,
        "has_cookieconsent": has_module("cookie_consent"),
        "has_mfa": has_module("mfa"),
        "has_gravatar": has_module("django_gravatar"),
        "has_session_security": has_module("session_security"),
        "has_oauth2_provider": has_module("oauth2_provider"),
        "show_app_library_button": show_app_library_button,
        "single_app_mode": not settings.MULTIPLE_APP_MODE,
        "configured_single_app": configured_single_app,
        "idp_backends": idps.keys(),
        "debug_mode": settings.DEBUG,
    }

    return context
