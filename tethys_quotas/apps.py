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
from django.db.utils import ProgrammingError, OperationalError
from tethys_quotas.utilities import sync_resource_quota_handlers

log = logging.getLogger("tethys." + __name__)


class TethysQuotasConfig(AppConfig):
    name = "tethys_quotas"
    verbose_name = "Tethys Quotas"

    def ready(self):
        try:
            sync_resource_quota_handlers()
        except (ProgrammingError, OperationalError) as e:
            if isinstance(e, ProgrammingError):
                log.warning(
                    "Unable to sync resource quota handlers: Resource Quota table does not exist"
                )
            elif isinstance(e, OperationalError):
                log.warning("Unable to sync resource quota handlers: No database found")
