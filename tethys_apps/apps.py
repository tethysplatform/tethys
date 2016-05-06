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

from tethys_apps.app_harvester import SingletonAppHarvester


class TethysAppsConfig(AppConfig):
    name = 'tethys_apps'
    verbose_name = 'Tethys Apps'

    def ready(self):
        """
        Startup method for Tethys Apps django app.
        """
        # Perform App Harvesting
        harvester = SingletonAppHarvester()
        harvester.harvest_apps()