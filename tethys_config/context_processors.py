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


def tethys_global_settings_context(request):
    """
    Add the current Tethys app metadata to the template context.
    """
    from .models import Setting
    from termsandconditions.models import TermsAndConditions

    # Get settings
    site_globals = Setting.as_dict()

    # Set default settings
    if not site_globals.get('primary_color'):
        site_globals['primary_color'] = '#0a62a9'

    if not site_globals.get('secondary_color'):
        site_globals['secondary_color'] = '#a2d6f9'

    if not site_globals.get('background_color'):
        site_globals['background_color'] = '#fefefe'

    if not site_globals.get('primary_text_color'):
        site_globals['primary_text_color'] = '#ffffff'

    if not site_globals.get('primary_text_hover_color'):
        site_globals['primary_text_hover_color'] = '#eeeeee'

    if not site_globals.get('secondary_text_color'):
        site_globals['secondary_text_color'] = '#212529'

    if not site_globals.get('secondary_text_hover_color'):
        site_globals['secondary_text_hover_color'] = '#aaaaaa'

    # Get terms and conditions
    site_globals.update({'documents': TermsAndConditions.get_active_terms_list()})

    context = {
        'site_globals': site_globals,
        'site_defaults': {
            'copyright': f'Copyright © {dt.datetime.utcnow():%Y} Your Organization',
        }
    }

    return context
