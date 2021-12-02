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
                'version': '3.6.0',
                'integrity': 'sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4=',

            },
            'bootstrap': {
                'version': '5.1.3',
                'css_integrity': 'sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3',
                'js_integrity': 'sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p'
            },
            'bootstrap_icons': {
                'version': '1.7.1',
            },
        }
    })

    return context
