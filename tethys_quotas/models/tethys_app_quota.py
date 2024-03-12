"""
********************************************************************************
* Name: tethys_app_quota.py
* Author: tbayer, mlebarron
* Created On: April 2, 2019
* Copyright: (c) Aquaveo 2018
********************************************************************************
"""

import logging

from django.db import models
from tethys_quotas.models.entity_quota import EntityQuota
from tethys_apps.models import TethysApp


log = logging.getLogger("tethys." + __name__)


class TethysAppQuota(EntityQuota):
    """
    entity_id (IntegerField): id of the entity.
    """

    class Meta:
        verbose_name = "Tethys App Quota"

    entity = models.ForeignKey(TethysApp, on_delete=models.CASCADE)
