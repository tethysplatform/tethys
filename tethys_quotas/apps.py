"""
********************************************************************************
* Name: apps.py
* Author: tbayer
* Created On: February 12, 2019
* Copyright: (c) Aquaveo 2018
********************************************************************************
"""
from django.apps import AppConfig
from tethys_quotas.helpers import sync_resource_quota_handlers


class TethysQuotasConfig(AppConfig):
    name = 'tethys_quotas'
    verbose_name = 'Tethys Quotas'

    def ready(self):
        sync_resource_quota_handlers()
