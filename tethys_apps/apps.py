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
import warnings
from django.apps import AppConfig

from tethys_apps.harvester import SingletonHarvester
from tethys_portal.cookies import sync_portal_cookies
from tethys_portal.optional_dependencies import has_module


class TethysAppsConfig(AppConfig):
    name = "tethys_apps"
    verbose_name = "Tethys Apps"

    def ready(self):
        """
        Startup method for Tethys Apps django app.
        """
        if len(sys.argv) > 1 and sys.argv[1] != "migrate":
            with warnings.catch_warnings():
                # syncing cookies, apps, and extensions with the database at startup
                # is intentional, so suppress Django's database access warning
                warnings.filterwarnings(
                    "ignore",
                    message="Accessing the database during app initialization",
                    category=RuntimeWarning,
                )
                if has_module("cookie_consent"):
                    sync_portal_cookies()
                # Perform App Harvesting (if database is not being migrated)
                harvester = SingletonHarvester()
                harvester.harvest()
