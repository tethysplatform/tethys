"""
********************************************************************************
* Name: context_processors.py
* Author: Nathan Swain, Riley Hales
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

    from django.core.management import settings

    # Setup variables
    context = {'tethys_app': None}

    # Get the app
    app = get_active_app(request=request)

    if app is not None:
        # Tethys app metadata
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

        # Web-Analytics services checks/Adding appropriate tags
        context['analytics'] = {
            'analytical': bool('analytical' in settings.INSTALLED_APPS),
            'clickmap': bool(settings.CLICKMAP_TRACKER_ID),
            'clicky': bool(settings.CLICKY_SITE_ID),
            'crazyegg': bool(settings.CRAZY_EGG_ACCOUNT_NUMBER),
            'gauges': bool(settings.GAUGES_SITE_ID),
            'googleanalytics': bool(settings.GOOGLE_ANALYTICS_JS_PROPERTY_ID),
            'gosquared': bool(settings.GOSQUARED_SITE_TOKEN),
            'hotjar': bool(settings.HOTJAR_SITE_ID),
            'hubspot': bool(settings.HUBSPOT_PORTAL_ID),
            'intercomio': bool(settings.INTERCOM_APP_ID),
            'kissinsights': bool(settings.KISSINSIGHTS_ACCOUNT_NUMBER and settings.KISSINSIGHTS_SITE_CODE),
            'kissmetrics': bool(settings.KISS_METRICS_API_KEY),
            'mixpanel': bool(settings.MIXPANEL_API_TOKEN),
            'olark': bool(settings.OLARK_SITE_ID),
            'optimizely': bool(settings.OPTIMIZELY_ACCOUNT_NUMBER),
            'performable': bool(settings.PERFORMABLE_API_KEY),
            'piwik': bool(settings.PIWIK_DOMAIN_PATH and settings.PIWIK_SITE_ID),
            'mailru': bool(settings.RATING_MAILRU_COUNTER_ID),
            'snapengage': bool(settings.SNAPENGAGE_WIDGET_ID),
            'springmetrics': bool(settings.SPRING_METRICS_TRACKING_ID),
            'uservote': bool(settings.USERVOICE_WIDGET_KEY),
            'woopra': bool(settings.WOOPRA_DOMAIN),
            'yandex': bool(settings.YANDEX_METRICA_COUNTER_ID),
        }

    return context
