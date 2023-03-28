"""
********************************************************************************
* Name: apps.py
* Author: Nathan Swain
* Created On: 2014
* Copyright:
* License: BSD 2-Clause
********************************************************************************
"""
import sys
from django.apps import AppConfig

from tethys_apps.harvester import SingletonHarvester


class TethysAppsConfig(AppConfig):
    name = "tethys_apps"
    verbose_name = "Tethys Apps"

    def ready(self):
        """
        Startup method for Tethys Apps django app.
        """
        if sys.argv[1] != "migrate":
            # Perform App Harvesting (if database is not being migrated)
            harvester = SingletonHarvester()
            harvester.harvest()
