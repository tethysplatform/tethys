"""
********************************************************************************
* Name: base.py
* Author: tbayer
* Created On: February 5, 2019
* Copyright: (c) Aquaveo 2018
********************************************************************************
"""

from abc import abstractmethod
from tethys_quotas.utilities import get_resource_available


class ResourceQuotaHandler(object):
    """
    Defines one or more ResourceQuotas. Also houses logic to check quota.

    Attributes:
        codename(str): unique codename for quota, used to look up specific quotas easily (e.g. ‘workspace_storage’).
        name(str): human friendly name of resource quota (e.g.: "Workspace Storage").
        description(str): more detailed description of the quota resource (e.g.: "Storage limit on workspaces.").
        default(int): default value (e.g. 10).
        units(str): units of the quota (e.g.: "GB").
        help(str): help text to display when quota is exceeded.
        applies_to(list<str>): list of dot-paths to the entities to which this quota will apply. Any of “django.contrib.auth.models.User” or “tethys_apps.models.TethysApp”.
        __init__(entity, args, kwargs): constructor
        entity(auth.User or TethysApp): the entity to evaluate.
    """  # noqa: E501

    codename = ""
    name = ""
    description = ""
    default = None
    units = ""
    help = ""
    applies_to = []

    def __init__(self, entity, *args, **kwargs):
        self.entity = entity

    @abstractmethod
    def get_current_use(self, *args, **kwargs):
        """
        Abstract method to be implemented by child classes. Should calculate/retrieve the current use of the resource (Int).
        """  # noqa: E501
        pass

    def check(self):
        """
        Checks if entity use is at/below/above quota. Uses get_resource_available() to compute the current use of the resource.

        Returns:
            Boolean: True if entity use is at or below quota and False if entity use is above the quota.
        """  # noqa: E501
        # self.codename isn't complete because the actual ResourceQuota codename is 'applies_to' specific
        codename = "{}_{}".format(self.entity.__class__.__name__.lower(), self.codename)
        resource_available = get_resource_available(self.entity, codename)
        if resource_available and resource_available["resource_available"] == 0:
            return False
        else:
            return True


class ResourceQuotaHandlerSub(ResourceQuotaHandler):
    # Class used for testing only. Will be implemented elsewhere later
    # tests will need refactoring when that happens.
    pass
