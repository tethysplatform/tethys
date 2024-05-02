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
from tethys_apps.utilities import get_configured_standalone_app


def tethys_portal_context(request):
    idps = (
        settings.SOCIAL_AUTH_SAML_ENABLED_IDPS
        if hasattr(settings, "SOCIAL_AUTH_SAML_ENABLED_IDPS")
        else {}
    )

    single_app_mode, configured_single_app = check_single_app_mode()

    context = {
        "has_analytical": has_module("analytical"),
        "has_terms": has_module("termsandconditions"),
        "has_mfa": has_module("mfa"),
        "has_gravatar": has_module("django_gravatar"),
        "has_session_security": has_module("session_security"),
        "has_oauth2_provider": has_module("oauth2_provider"),
        "single_app_mode": single_app_mode,
        "configured_single_app": configured_single_app,
        "idp_backends": idps.keys(),
    }

    return context


def check_single_app_mode():
    if settings.MULTIPLE_APP_MODE:
        return False, None
    else:
        return True, get_configured_standalone_app()
