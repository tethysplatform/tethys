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

    # Dependency Versions
    context.update({
        'tethys': {
            'jquery': {
                'version': '3.5.1',
                'integrity': 'sha256-9/aliU8dGd2tb6OSsuzixeV4y/faTqgFtohetphbbj0=',

            },
            'bootstrap': {
                'version': '3.4.1',
                'css_integrity': 'sha384-HSMxcRTRxnN+Bdg0JdbxYKrThecOKuH5zCYotlSAcp1+c8xmyTe9GYg1l9a69psu',
                'js_integrity': 'sha384-aJ21OjlMXNL5UyIl/XNwTMqvzeRMZH2w8c5cRVpzpU8Y5bApTppSuUkhZXN0VxHd'
            },
        }
    })

    return context
