"""
********************************************************************************
* Name: context_processors.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
from .models import Setting


def tethys_global_settings_context(request):
    """
    Add the current Tethys app metadata to the template context.
    """

    # Get settings
    settings = Setting.as_dict()

    context = {'site_globals': settings}

    return context
