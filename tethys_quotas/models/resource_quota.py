"""
********************************************************************************
* Name: resource_quota.py
* Author: tbayer, glarsen
* Created On: January 24, 2019
* Copyright: (c) Aquaveo 2018
********************************************************************************
"""

import logging
import inspect
from django.contrib.auth.models import User
from django.db import models
from tethys_apps.base.function_extractor import TethysFunctionExtractor
from tethys_apps.models import TethysApp
from tethys_quotas.handlers.base import ResourceQuotaHandler


log = logging.getLogger("tethys." + __name__)


class ResourceQuota(models.Model):
    """
    Model definition for all quota types. This is intended to be an internal class that is not directly instantiated by users.

    Attributes:
        codename (CharField): unique codename for quota, used to look up specific quotas easily (e.g. ‘workspace_storage’).
        name (CharField): human friendly name of resource quota (e.g.: "Workspace Storage").
        description (TextField): more detailed description of the quota resource (e.g.: "Storage limit on workspaces.").
        default (DoubleField): default value (e.g. 10).
        units (CharField): units of the quota (e.g.: "GB").
        applies_to (TextField): type of entity to which this instance of the quota applies. Value should be a dot-path to the entity class. One of “django.contrib.auth.models.User” or “tethys_apps.models.TethysApp”.
        active (BooleanField): whether the quota is being enforced or not. Defaults to False.
        impose_default (BooleanField): Apply default to all applies_to entities that don’t have individual quotas applied. Defaults to True.
        help (TextField): help text to display when quota is exceeded.
        _handler (CharField): a dot-path to the ResourceQuotaHandler class (e.g.: “tethys_quotas.handlers.WorkspaceQuotaHandler”)
    """  # noqa: E501

    class Meta:
        verbose_name = "Resource Quota"

    codename = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=2048, blank=True, default="")
    default = models.FloatField()
    units = models.CharField(max_length=100)
    applies_to = models.TextField()
    active = models.BooleanField(default=False)
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
        quota_obj = TethysFunctionExtractor(self._handler, prefix="")
        return quota_obj.function

    @handler.setter
    def handler(self, class_path):
        """
        Method to set the handler. Checks to make sure handler is valid.

        Args:
            class_path (str or class): handler class string or instance
        """
        if isinstance(class_path, str):
            obj = TethysFunctionExtractor(class_path, prefix="")
            if obj.function and issubclass(obj.function, ResourceQuotaHandler):
                self._handler = class_path
            else:
                raise ValueError(
                    "{} must be a subclass of ResourceQuotaHandler".format(class_path)
                )
        elif inspect.isclass(class_path):
            if issubclass(class_path, ResourceQuotaHandler):
                self._handler = "{}.{}".format(
                    class_path.__module__, class_path.__name__
                )
            else:
                raise ValueError(
                    "{} must be a subclass of ResourceQuotaHandler".format(class_path)
                )

    def check_quota(self, entity):
        """
        uses associated ResourceQuotaHandler to perform the quota check on the given entity

        Args:
            entity (auth): the entity to evaluate

        Returns:
            Boolean: check passes or fails**
        """
        not_app_instance = not isinstance(entity, TethysApp)
        not_app_class = not (inspect.isclass(entity) and issubclass(entity, TethysApp))
        not_user = not isinstance(entity, User)

        if not_user and not_app_instance and not_app_class:
            raise ValueError("{} must be a django User or TethysApp".format(entity))
        RQH = self.handler
        resource_quota_handler = RQH(entity)
        return resource_quota_handler.check()

    def __str__(self):
        return self.name
