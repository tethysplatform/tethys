from django.conf.urls import url

from tethys_apps.harvesters.app_harvester import SingletonAppHarvester


def generate_app_url_patterns():
    """
    Generate the url pattern lists for each app and namespace them accordingly.
    """

    # Get controllers list from app harvester
    harvester = SingletonAppHarvester()
    controllers = harvester.controllers

    app_url_patterns = dict()

    for controller in controllers:
        app_root = controller['root']
        app_namespace = app_root.replace('-', '_')

        if app_namespace not in app_url_patterns:
            app_url_patterns[app_namespace] = []

        # Create django url object
        django_url = url(controller['url'], controller['controller'], name=controller['name'])

        # Append to namespace list
        app_url_patterns[app_namespace].append(django_url)

    return app_url_patterns

