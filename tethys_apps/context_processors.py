"""
********************************************************************************
* Name: context_processors.py
* Author: Nathan Swain
* Created On: 2014
* Copyright: (c) Brigham Young University 2014
* License: BSD 2-Clause
********************************************************************************
"""
from tethys_apps.utilities import get_active_app


def tethys_apps_context(request):
    """
    Add the current Tethys app metadata to the template context.

    Enables web-analytics services by:
        1. Checking which analytics services are configured for the portal
        2. Creates a string with the necessary tags to load each of the web-analytics services
        3. Puts them in a dictionary which can be read as a variable in the app_base.html template

    Args:
        request: Django request object.
    """

    # Setup variables
    context = {'tethys_app': None}

    # Get the app
    app = get_active_app(request=request)

    if app is not None:
        context['tethys_app'] = {
            'id': app.id,
            'name': app.name,
            'index': app.index,
            'icon': app.icon,
            'color': app.color,
            'tags': app.tags,
            'description': app.description,
            'namespace': app.namespace
        }

        if hasattr(app, 'feedback_emails') and len(app.feedback_emails) > 0:
            context['tethys_app']['feedback_emails'] = app.feedback_emails

            if hasattr(app, 'enable_feedback'):
                context['tethys_app']['enable_feedback'] = app.enable_feedback

    return context
