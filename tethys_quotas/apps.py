"""
********************************************************************************
* Name: apps.py
* Author: tbayer
* Created On: February 12, 2019
* Copyright: (c) Aquaveo 2018
********************************************************************************
"""
import logging
from django.apps import AppConfig
from tethys_quotas.helpers import sync_resource_quota_handlers

log = logging.getLogger('tethys.' + __name__)


class TethysQuotasConfig(AppConfig):
    name = 'tethys_quotas'
    verbose_name = 'Tethys Quotas'

    def ready(self):
        try:
            sync_resource_quota_handlers()
        except:  # noqa
            log.warning("RQ table not created yet")
