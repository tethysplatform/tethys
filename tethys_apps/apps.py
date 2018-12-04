"""
********************************************************************************
* Name: apps.py
* Author: Nathan Swain
* Created On: 2014
* Copyright:
* License: BSD 2-Clause
********************************************************************************
"""
from django.apps import AppConfig

from tethys_apps.harvester import SingletonHarvester


class TethysAppsConfig(AppConfig):
    name = 'tethys_apps'
    verbose_name = 'Tethys Apps'
    harvester = SingletonHarvester()

    def import_models(self):
        """
        Import models
        """
        # Load models for the tethys_apps app
        super(TethysAppsConfig, self).import_models()

        # Perform App Harvesting
        self.harvester.harvest()

        # Load models for tethys apps and extensions
        custom_django_models = []
        for app in self.harvester.apps:
            custom_django_models.extend(app.django_models())

        for ext in self.harvester.extensions:
            custom_django_models.extend(ext.django_models())

        for model in custom_django_models:
            # TODO: Import models from string...
            self.models[model.__name__.lower()] = model


    def ready(self):
        """
        Startup method for Tethys Apps django app.
        """
        # Synchronize with tethys db
        self.harvester.sync_with_db()
