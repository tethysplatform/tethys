"""
********************************************************************************
* Name: entity_quota.py
* Author: tbayer, glarsen
* Created On: January 31, 2019
* Copyright: (c) Aquaveo 2018
********************************************************************************
"""
import logging

from django.db import models
from model_utils.managers import InheritanceManager

from tethys_quotas.models.resource_quota import ResourceQuota


log = logging.getLogger('tethys.' + __name__)


class EntityQuota(models.Model):
    """
    An intermediate model that maps between the ResourceQuota model and the auth.User model or TethysApp

    resource_quota_id (ForeignKeyField): id of the quota
    value (IntegerField): value of the quota.
    active (BooleanField): whether the quota is being enforced or not. Defaults to True.
    """  # noqa: E501

    class Meta:
        verbose_name = 'Entity Quota'

    objects = InheritanceManager()

    resource_quota = models.ForeignKey(ResourceQuota, on_delete=models.CASCADE)
    value = models.IntegerField(null=True, blank=True)
