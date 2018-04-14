"""
********************************************************************************
* Name: context_processors.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""


def tethys_global_settings_context(request):
    """
    Add the current Tethys app metadata to the template context.
    """
    from .models import Setting
    from termsandconditions.models import TermsAndConditions

    # Get settings
    site_globals = Setting.as_dict()

    # Get terms and conditions

    # Grrr!!! TermsAndConditions has a different interface for Python 2 and 3
    try:
        # for Python 3
        site_globals.update({'documents': TermsAndConditions.get_active_terms_list()})
    except AttributeError:
        # for Python 3
        site_globals.update({'documents': TermsAndConditions.get_active_list(as_dict=False)})

    context = {'site_globals': site_globals}

    return context
