"""
********************************************************************************
* Name: resource_quota.py
* Author: tbayer, glarsen
* Created On: January 24, 2019
* Copyright: (c) Aquaveo 2018
********************************************************************************
"""
import logging

from django.db import models
from model_utils.managers import InheritanceManager


log = logging.getLogger('tethys.' + __name__)

class ResourceQuota(models.Model):
    """
    Base class for all quota types. This is intended to be an abstract class that is not directly instantiated.

    codename (CharField): unique codename for quota, used to look up specific quotas easily (e.g. ‘workspace_storage’).
    name (CharField): human friendly name of resource quota (e.g.: "Workspace Storage").
    description (TextField): more detailed description of the quota resource (e.g.: "Storage limit on workspaces.").
    default (DoubleField): default value (e.g. 10).
    units (CharField): units of the quota (e.g.: "GB").
    help (TextField): help text to display when quota is exceeded.
    applies_to (TextField): type of entity to which this instance of the quota applies. Value should be a dot-path to the entity class. One of “django.contrib.auth.models.User” or “tethys_apps.models.TethysApp”.
    active (BooleanField): whether the quota is being enforced or not. Defaults to False.
    impose_default (BooleanField): Apply default to all applies_to entities that don’t have individual quotas applied. Defaults to True.
    _handler (CharField): a dot-path to the ResourceQuotaHandler class (e.g.: “tethys_quotas.handlers.WorkspaceQuotaHandler”)
    """
    class Meta:
        verbose_name = 'Quota'

    objects = InheritanceManager()

    codename = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=2048, blank=True, default='')
    default = models.FloatField()
    units = models.CharField(max_length=100)
    applies_to = models.TextField()
    impose_default = models.BooleanField(default=True)
    help = models.TextField()
    _handler = models.TextField()

    @property
    def handler(self):
        """
        property containing the resource handler class

        Returns:
            ResourceQuotaHandler class
        """
        raise NotImplemented('Handler property net yet implemented')

    def check_quota(self, entity):
        """
        uses associated ResourceQuotaHandler to perform the quota check on the given entity

        Args:
            entity (auth): the entity to evaluate

        Returns:
            Boolean: check passes or fails**
        """
        raise NotImplemented('check_quota function net yet implemented')


