"""
********************************************************************************
* Name: apps.py
* Author: Michael Souffront
* Created On: 2025
* License: BSD 2-Clause
********************************************************************************
"""

from django.apps import AppConfig
from tethys_portal.optional_dependencies import has_module


if has_module("django_tenants"):

    class TethysTenantsConfig(AppConfig):
        name = "tethys_tenants"
        verbose_name = "Tethys Tenants"

        def ready(self):
            import tethys_tenants.checks  # noqa: F401
