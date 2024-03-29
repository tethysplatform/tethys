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


def tethys_portal_context(request):
    context = {
        "has_analytical": has_module("analytical"),
        "has_recaptcha": has_module("snowpenguin.django.recaptcha2"),
        "has_terms": has_module("termsandconditions"),
        "has_mfa": has_module("mfa"),
        "has_gravatar": has_module("django_gravatar"),
        "has_session_security": has_module("session_security"),
        "has_oauth2_provider": has_module("oauth2_provider"),
    }

    return context
