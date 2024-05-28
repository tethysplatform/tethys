"""
********************************************************************************
* Name: user_quota.py
* Author: tbayer, mlebarron
* Created On: March 2, 2019
* Copyright: (c) Aquaveo 2018
********************************************************************************
"""

import logging

from django.db import models
from django.contrib.auth.models import User
from tethys_quotas.models.entity_quota import EntityQuota


log = logging.getLogger("tethys." + __name__)


class UserQuota(EntityQuota):
    """
    entity_id (IntegerField): id of the entity.
    """

    class Meta:
        verbose_name = "User Quota"

    entity = models.ForeignKey(User, on_delete=models.CASCADE)
